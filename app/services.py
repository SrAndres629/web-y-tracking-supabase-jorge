class ContentManager:
    def __init__(self):
        self._FALLBACKS = {
            'service1': {
                'badge': 'badge1.png',
                'image': 'image1.png',
                'rating': 4.5,
                'clients': 120,
                'benefits': ['Benefit 1', 'Benefit 2'],
                'subtitle': 'Subtitle 1'
            },
            'service2': {
                'badge': 'badge2.png',
                'image': 'image2.png',
                'rating': 4.2,
                'clients': 98,
                'benefits': ['Benefit 3', 'Benefit 4'],
                'subtitle': 'Subtitle 2'
            },
            'service3': {
                'badge': 'badge3.png',
                'image': 'image3.png',
                'rating': 4.8,
                'clients': 150,
                'benefits': ['Benefit 5', 'Benefit 6'],
                'subtitle': 'Subtitle 3'
            }
        }

    # Other method definitions of the ContentManager class would be here

