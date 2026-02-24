from app.services import _normalize_service_image_path


def test_normalize_legacy_static_images_prefix():
    assert (
        _normalize_service_image_path("/static/images/service_eyes.webp")
        == "/static/assets/images/service_eyes.webp"
    )


def test_normalize_relative_legacy_prefix():
    assert (
        _normalize_service_image_path("static/images/service_brows.webp")
        == "/static/assets/images/service_brows.webp"
    )


def test_keep_modern_assets_prefix_unchanged():
    assert (
        _normalize_service_image_path("/static/assets/images/service_lips.webp")
        == "/static/assets/images/service_lips.webp"
    )
