import os
import re
import glob
from bs4 import BeautifulSoup

def audit_html_semantics(html_templates_path):
    """
    Audits HTML templates for common semantic and accessibility issues.

    Args:
        html_templates_path (str): Path to the directory containing HTML templates.

    Returns:
        dict: A dictionary containing lists of identified issues.
    """
    issues = {
        "images_without_alt": [],
        "links_without_href": [],
        "buttons_without_type": [],
        "elements_with_positive_tabindex": [],
        "empty_headings": [],
        "heading_level_skips": [] # More complex, will implement if time/resources allow
    }

    html_files = glob.glob(os.path.join(html_templates_path, '**', '*.html'), recursive=True)

    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
            
            # --- Check 1: Images without alt attribute ---
            for img in soup.find_all('img'):
                if img.get('alt') is None:
                    issues["images_without_alt"].append(f"{html_file}: <img src='{img.get('src', 'N/A')}' missing alt attribute>")

            # --- Check 2: Links without href attribute ---
            for a in soup.find_all('a'):
                if not a.get('href') and a.text.strip(): # Only report if it has content but no href
                    issues["links_without_href"].append(f"{html_file}: <a> tag with text '{a.text.strip()}' missing href attribute")

            # --- Check 3: Buttons without type attribute ---
            for button in soup.find_all('button'):
                if not button.get('type'):
                    issues["buttons_without_type"].append(f"{html_file}: <button> tag with text '{button.text.strip()}' missing type attribute")
            
            # --- Check 4: Elements with positive tabindex ---
            for el in soup.find_all(tabindex=re.compile(r'^[1-9]\d*$')): # tabindex > 0
                issues["elements_with_positive_tabindex"].append(f"{html_file}: <{el.name}> tag with positive tabindex='{el.get('tabindex')}' found. Prefer tabindex='0' or none.")

            # --- Check 5: Empty Headings ---
            for h_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                for h in soup.find_all(h_tag):
                    if not h.text.strip():
                        issues["empty_headings"].append(f"{html_file}: <{h_tag}> tag is empty.")

            # --- Check 6: Heading Level Skips (Basic) ---
            # This is a complex check to do perfectly, but a basic check can be done.
            # Find all headings and sort by their position in the document.
            headings = []
            for h_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                for h in soup.find_all(h_tag):
                    # Store as (level, element)
                    headings.append((int(h_tag[1]), h))
            
            # Sort by approximate document order (not perfect without actual DOM tree traversal)
            # For simplicity, we'll just check if current level is more than 1 greater than previous
            last_level = 0
            for level, h_element in sorted(headings, key=lambda x: str(x[1])): # Sort by element's string representation for basic ordering
                 if last_level == 0: # First heading found
                     last_level = level
                     continue
                 if level > last_level + 1:
                     issues["heading_level_skips"].append(f"{html_file}: Heading level skipped from H{last_level} to H{level} for text '{h_element.text.strip()}'")
                 last_level = level

    # Filter out empty issue lists
    return {k: v for k, v in issues.items() if v}

if __name__ == "__main__":
    HTML_TEMPLATES_PATH = 'api/templates/'

    if not os.path.exists(HTML_TEMPLATES_PATH):
        print(f"Error: HTML templates path not found: {HTML_TEMPLATES_PATH}")
    else:
        print(f"Auditing HTML semantic and accessibility issues in '{HTML_TEMPLATES_PATH}'...")
        all_issues = audit_html_semantics(HTML_TEMPLATES_PATH)

        if all_issues:
            print("\n🚨 HTML Semantic and Accessibility Issues Found:")
            for issue_type, issue_list in all_issues.items():
                print(f"\n--- {issue_type.replace('_', ' ').title()} ({len(issue_list)} issues) ---")
                for issue in issue_list:
                    print(f"  - {issue}")
            print(f"\nTotal issue categories found: {len(all_issues)}")
        else:
            print("\n✅ No significant HTML semantic or accessibility issues found. Great job!")