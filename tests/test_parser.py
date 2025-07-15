from signature_recovery.core.parser import SignatureParser

examples = [
    (
        "John Doe\nEngineer\nACME Inc.\n555-555-1234\njohn@example.com\nwww.acme.com\n123 Main St, Springfield, IL 62704",
        {
            "name": "John Doe",
            "title": "Engineer",
            "company": "ACME Inc.",
            "phone": "555-555-1234",
            "email": "john@example.com",
            "url": "www.acme.com",
            "address": "123 Main St, Springfield, IL 62704",
        },
    ),
    (
        "Jane Smith | Manager | Example LLC\nPhone: 123.456.7890\nEmail: jane@ex.com",
        {
            "name": "Jane Smith",
            "title": "Manager",
            "company": "Example LLC",
            "phone": "123.456.7890",
            "email": "jane@ex.com",
        },
    ),
    (
        "Bob Brown\nDirector\nBig Co\n(555) 321-0000\nbob@big.co",
        {
            "name": "Bob Brown",
            "title": "Director",
            "company": "Big Co",
            "phone": "(555) 321-0000",
            "email": "bob@big.co",
        },
    ),
    (
        "Alice White\nConsultant\nWHITE LLC\nwww.white.com",
        {
            "name": "Alice White",
            "title": "Consultant",
            "company": "WHITE LLC",
            "url": "www.white.com",
        },
    ),
    (
        "Carlos Green\nEngineer\nTechCorp Inc\n+1 555 777 8888",
        {
            "name": "Carlos Green",
            "title": "Engineer",
            "company": "TechCorp Inc",
            "phone": "+1 555 777 8888",
        },
    ),
    (
        "Eve Black\nManager\nBlack Ltd\n123 Market Ave, Gotham, NY",
        {
            "name": "Eve Black",
            "title": "Manager",
            "company": "Black Ltd",
            "address": "123 Market Ave, Gotham, NY",
        },
    ),
    (
        "Frank Stone\nProduct Officer\nStone Corp\nfrank.stone@stone.com",
        {
            "name": "Frank Stone",
            "title": "Product Officer",
            "company": "Stone Corp",
            "email": "frank.stone@stone.com",
        },
    ),
    (
        "Grace Lee\nEngineer\n555-000-1111",
        {
            "name": "Grace Lee",
            "title": "Engineer",
            "phone": "555-000-1111",
        },
    ),
    (
        "Henry Young\nDirector\nYOUNG LLC\nwww.young.com\nhenry@young.com",
        {
            "name": "Henry Young",
            "title": "Director",
            "company": "YOUNG LLC",
            "url": "www.young.com",
            "email": "henry@young.com",
        },
    ),
    (
        "Irene Adler\nConsultant\nAdler Consulting\n+44 20 1234 5678\nhttp://adler.co.uk",
        {
            "name": "Irene Adler",
            "title": "Consultant",
            "company": "Adler Consulting",
            "phone": "+44 20 1234 5678",
            "url": "http://adler.co.uk",
        },
    ),
]


def test_parser_examples():
    parser = SignatureParser()
    for text, expected in examples:
        meta = parser.parse(text)
        for key, val in expected.items():
            assert getattr(meta, key) == val
