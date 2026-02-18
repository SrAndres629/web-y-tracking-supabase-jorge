# 🎯 SKILL: Meta Signal Maximizer (CPA Crusher)

## Objective
To lower CPA (Cost Per Action) by feeding Meta's AI with "High-Fidelity" data, allowing it to bid more efficiently for users.

## 1. The Strategy: "Signal Density"
Meta's algorithm penalizes advertisers with poor data. We will gain a "Data Discount" by providing:
*   **fbp**: Browser ID (Cookie).
*   **fbc**: Click ID (URL Parameter).
*   **UserData**: Hashed Email/Phone.

## 2. Implementation Logic (Python/FastAPI)

### A. The "Ghost" Pixel (Server-Side)
Logic: When a user submits a form, the browser may block the JS Pixel. The Server MUST send the event concurrently.
```python
# Pseudo-code for Mental Model
def handle_form_submit(data: LeadForm):
    # 1. Save to DB (Primary)
    db.save(data)

    # 2. Fire CAPI Event (Async)
    capi.send_event(
        event_name="Lead",
        user_data={
            "em": hash(data.email),
            "ph": hash(data.phone),
            "client_ip": request.ip,
            "fbc": request.cookies.get("_fbc")
        }
    )
```

## 3. Deduplication Key
Crucial: To avoid double-counting (and inflating CPA reports), we must generate an `event_id` in the frontend, pass it to the server, and send it to both Browser Pixel and CAPI.

## 4. Economic Impact
*   **Higher Match Quality** = Meta trusts your conversion data more.
*   **Better Trust** = Meta shows ads to "lookalikes" with higher confidence.
*   **Result** = Cheaper CPMs and higher CTRs (Lower CPA).
