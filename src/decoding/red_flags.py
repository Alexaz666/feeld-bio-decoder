RED_FLAG_CATEGORIES = {
    "structure": [
        "a couple",
        "my partner and i",
        "my wife and i",
        "my husband and i",
        "for my partner",
        "joining us",
        "join us",
        "play together",
        "a third",
        "unicorn",
        "sinlge female",
        "open marriage",
        "we're"
    ],
    "tone": [
        "just ask",
        "open book",
        "open to anything",
        "play games",
        "fuck spiders",
        "no drama",
        "drama free",
        "time wasters",
        "alpha",
        "leader"
    ],
    "discriminatory": [
        "fatties",
        "coloured", "colored",
        "real women", "real woman",
        "feminine women", "feminine woman",
        "traditional women", "traditional woman",
        "conservative women", "conservative woman",
        "wife material",
        "sjw",
        "woke",
    ],
    "sexual_intent_mismatch": [
        "dtf",
        "ons ",
        "nsa",
        "no strings",
        "no feelings",
        "high sex drive",
        "for anything serious",
        "not a long time",
        "discreet",
    ]
}

def flag_red_phrases(text: str) -> list:
    text = text.lower()
    flags = []
    for category, phrases in RED_FLAG_CATEGORIES.items():
        for phrase in phrases:
            if phrase in text:
                flags.append({"type": category, "phrase": phrase})
    return flags
