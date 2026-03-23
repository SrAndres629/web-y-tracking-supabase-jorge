import re

with open("api/templates/components/footer.html", "r") as f:
    footer = f.read()

assert 'aria-label="Facebook"' in footer
assert 'aria-label="Instagram"' in footer
assert 'aria-label="TikTok"' in footer
assert '<i class="fab fa-facebook-f" aria-hidden="true"></i>' in footer
assert '<i class="fab fa-instagram" aria-hidden="true"></i>' in footer
assert '<i class="fab fa-tiktok" aria-hidden="true"></i>' in footer
assert '<i class="fab fa-whatsapp" aria-hidden="true"></i>' in footer
assert 'aria-label="Contactar por WhatsApp"' in footer

with open("api/templates/components/navbar.html", "r") as f:
    navbar = f.read()

assert 'aria-label="Cerrar menú"' in navbar
assert '<span aria-hidden="true">&times;</span>' in navbar
assert '<i class="fas fa-bars" aria-hidden="true"></i>' in navbar
assert '<i class="fab fa-whatsapp" aria-hidden="true"></i>' in navbar

print("A11y tests passed!")
