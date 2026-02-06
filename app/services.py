services_config = {
    'service_1': {
        'badges': ['badge1', 'badge2'],
        'image': 'path/to/image1.jpg',
        'rating': 4.5,
        'clients': ['client1', 'client2'],
        'benefits': ['benefit1', 'benefit2'],
        'subtitle': 'Subtitle for service 1'
    },
    'service_2': {
        'badges': ['badge3'],
        'image': 'path/to/image2.jpg',
        'rating': 5.0,
        'clients': ['client3'],
        'benefits': ['benefit3', 'benefit4'],
        'subtitle': 'Subtitle for service 2'
    },
    'service_3': {
        'badges': [],
        'image': 'path/to/image3.jpg',
        'rating': 3.5,
        'clients': ['client4', 'client5'],
        'benefits': ['benefit5'],
        'subtitle': 'Subtitle for service 3'
    }
}

# Replace _FALLBACKS dictionary with complete service data structures
_FALLBACKS = services_config
