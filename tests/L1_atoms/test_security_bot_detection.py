from unittest.mock import MagicMock

from app.middleware.security import SecurityHeadersMiddleware


def test_bot_detection_regex():
    """
    Test that the bot detection regex correctly identifies common bots and distinguishes them from human user agents.
    """
    # Mock the app for middleware initialization
    mock_app = MagicMock()
    middleware = SecurityHeadersMiddleware(mock_app)

    # List of known bot user agents
    bot_user_agents = [
        "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
        "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
        "DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)",
        "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
        "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
        "Twitterbot/1.0",
        "LinkedInBot/1.0 (compatible; Mozilla/5.0; Jakarta Commons-HttpClient/3.1 +http://www.linkedin.com)",
        "Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)",
        "Pinterest/0.2 (+http://www.pinterest.com/bot.html)",
        "Mozilla/5.0 (compatible; Embedly/0.2; +http://support.embed.ly/)",
        "Quora Link Preview/1.8.0 (http://www.quora.com)",
        "ShowyouBot (http://showyou.com/crawler)",
        "Outbrain/1.0 (http://www.outbrain.com)",
        "vkShare; +http://vk.com/dev/Share",
        "W3C_Validator/1.3 http://validator.w3.org/services",
        "UptimeRobot/2.0 (http://www.uptimerobot.com/)",
        "Monitor.Us (http://www.monitor.us)",
        "Screaming Frog SEO Spider/12.6",
        "Mozilla/5.0 (compatible; MJ12bot/v1.4.8; http://mj12bot.com/)",
        "Rogerbot/1.0 (http://moz.com/help/pro/moz-analytics/rogerbot-crawler)",
    ]

    # List of known human user agents
    human_user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36",
    ]

    # Test bots
    for agent in bot_user_agents:
        assert middleware.bot_pattern.search(agent), f"Failed to identify bot: {agent}"

    # Test humans
    for agent in human_user_agents:
        assert not middleware.bot_pattern.search(agent), f"Incorrectly identified human as bot: {agent}"
