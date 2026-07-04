from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import re

analyzer = SentimentIntensityAnalyzer()

EMOTIONS = [
    'Sadness',
    'Melancholy',
    'Nostalgia',
    'Calmness',
    'Loneliness',
    'Anxiety',
    'Hopefulness',
    'Excitement',
    'Anger',
    'Confidence',
    'Romantic Warmth',
    'Energy',
    'Introspection',
    'Serenity',
    'Motivation',
    'Burnout',
    'Mental Fatigue',
    'Hopelessness',
    'Emotional Numbness',
    'Existential Emptiness',
    'Quiet Healing',
    'Grief Acceptance',
    'Late Night Overthinking',
    'Euphoric Confidence',
    'Emotional Suppression',
    'Quiet Sadness',
    'Fragile Hope'
]

EMOTION_LEXICON = {
    'Sadness': {
        'sad': 28, 'down': 18, 'hurt': 22, 'cry': 30, 'tears': 30, 'broken': 26,
        'heartbroken': 42, 'grief': 38, 'empty': 22, 'depressed': 34, 'tired': 12,
        'drained': 18, 'miss': 20, 'missing': 24, 'rejected': 24, 'rejection': 28
    },
    'Melancholy': {
        'melancholy': 42, 'rain': 24, 'rainy': 26, 'window': 16, 'grey': 18,
        'gray': 18, 'quiet': 16, 'night': 15, 'midnight': 18, 'soft': 10,
        'slow': 10, 'alone': 14, 'memory': 18, 'memories': 20, 'watching': 10
    },
    'Nostalgia': {
        'nostalgic': 44, 'remember': 26, 'memory': 28, 'memories': 30, 'miss': 24,
        'past': 18, 'summer': 16, 'childhood': 30, 'again': 10, 'old': 12,
        'used': 10, 'her': 10, 'him': 10, 'home': 12
    },
    'Calmness': {
        'calm': 36, 'quiet': 22, 'still': 22, 'peaceful': 34, 'gentle': 24,
        'soft': 18, 'watching': 14, 'rain': 18, 'breathe': 22, 'relaxed': 32,
        'chill': 34, 'slow': 16, 'window': 12
    },
    'Loneliness': {
        'lonely': 42, 'alone': 34, 'isolated': 34, 'empty': 24, 'apart': 20,
        'miss': 18, 'missing': 22, 'solitude': 26, 'nobody': 26, 'distant': 20,
        'her': 8, 'him': 8
    },
    'Anxiety': {
        'anxious': 42, 'anxiety': 44, 'worried': 34, 'nervous': 30, 'panic': 42,
        'overthinking': 34, 'restless': 24, 'scared': 30, 'afraid': 30,
        'stress': 26, 'stressed': 30, 'uneasy': 28
    },
    'Hopefulness': {
        'okay': 28, 'hope': 38, 'hopeful': 42, 'better': 24, 'heal': 28,
        'healing': 32, 'soon': 12, 'tomorrow': 14, 'brighter': 24,
        'believe': 22, 'will': 8, 'can': 8
    },
    'Excitement': {
        'excited': 42, 'electric': 38, 'alive': 30, 'hype': 34, 'wild': 28,
        'tonight': 14, 'rush': 26, 'thrilled': 42, 'amazing': 28, 'awesome': 26,
        'unstoppable': 24
    },
    'Anger': {
        'angry': 46, 'mad': 38, 'furious': 48, 'rage': 48, 'hate': 42,
        'pissed': 40, 'annoyed': 30, 'irritated': 32, 'frustrated': 34,
        'betrayed': 28
    },
    'Confidence': {
        'confident': 42, 'unstoppable': 48, 'strong': 30, 'powerful': 34,
        'ready': 22, 'brave': 26, 'bold': 26, 'certain': 24, 'win': 24,
        'winning': 28
    },
    'Romantic Warmth': {
        'love': 38, 'lover': 30, 'romantic': 42, 'heart': 24, 'her': 8,
        'him': 8, 'kiss': 32, 'together': 24, 'intimate': 34, 'warm': 20,
        'miss': 10
    },
    'Energy': {
        'energy': 40, 'energetic': 42, 'move': 26, 'dance': 34, 'run': 22,
        'gym': 24, 'fast': 20, 'wired': 30, 'pumped': 38, 'electric': 34,
        'unstoppable': 26
    },
    'Introspection': {
        'thinking': 30, 'overthinking': 34, 'reflect': 34, 'reflection': 36,
        'inside': 20, 'mind': 18, 'deep': 22, 'watching': 22, 'window': 18,
        'quiet': 18, 'alone': 18, 'wonder': 22
    },
    'Serenity': {
        'serene': 42, 'peaceful': 34, 'still': 28, 'breathe': 28, 'gentle': 22,
        'calm': 28, 'soft': 20, 'rain': 12, 'floating': 22, 'safe': 20
    },
    'Motivation': {
        'motivated': 44, 'focus': 30, 'focused': 32, 'ready': 24, 'goal': 24,
        'grind': 26, 'work': 16, 'build': 18, 'driven': 38, 'discipline': 28,
        'unstoppable': 34
    },
    'Burnout': {
        'burnout': 52, 'burned': 38, 'exhausted': 44, 'drained': 38, 'tired': 34,
        'fatigued': 42, 'overwhelmed': 36, 'done': 24, 'everything': 16, 'numb': 20
    },
    'Mental Fatigue': {
        'tired': 36, 'exhausted': 36, 'drained': 34, 'fatigue': 44, 'foggy': 32,
        'heavy': 28, 'overloaded': 38, 'overwhelmed': 30, 'brain': 18, 'mind': 16
    },
    'Hopelessness': {
        'hopeless': 52, 'pointless': 44, 'nothing': 32, 'everything': 18, 'give': 18,
        'quit': 26, 'lost': 28, 'meaningless': 46, 'empty': 32, 'tired': 16
    },
    'Emotional Numbness': {
        'numb': 54, 'empty': 36, 'blank': 34, 'nothing': 28, 'feel': 12,
        'feeling': 12, 'detached': 36, 'distant': 26, 'hollow': 42
    },
    'Existential Emptiness': {
        'meaningless': 52, 'purpose': 26, 'pointless': 42, 'existential': 54,
        'empty': 34, 'void': 44, 'why': 20, 'everything': 18
    },
    'Quiet Healing': {
        'healing': 42, 'heal': 34, 'trying': 26, 'calm': 24, 'accept': 30,
        'acceptance': 38, 'breathe': 24, 'okay': 28, 'gentle': 16
    },
    'Grief Acceptance': {
        'grief': 48, 'loss': 42, 'lost': 28, 'accept': 30, 'acceptance': 36,
        'goodbye': 34, 'miss': 24, 'remember': 18, 'peace': 22
    },
    'Late Night Overthinking': {
        'overthinking': 50, 'thinking': 26, 'sleep': 20, 'sleepless': 38,
        'night': 24, 'midnight': 32, '2am': 38, '3am': 38, 'mind': 20
    },
    'Euphoric Confidence': {
        'unstoppable': 52, 'euphoric': 52, 'invincible': 46, 'powerful': 32,
        'alive': 34, 'winning': 34, 'ready': 24, 'hype': 28
    },
    'Emotional Suppression': {
        'fine': 18, 'okay': 16, 'talk': 18, 'hide': 34, 'pretend': 38, 'suppress': 48,
        'bottle': 34, 'silent': 28, 'private': 22, 'mask': 34
    },
    'Quiet Sadness': {
        'okay': 10, 'quiet': 24, 'sad': 24, 'tired': 16, 'soft': 14, 'alone': 18
    },
    'Fragile Hope': {
        'trying': 28, 'hope': 28, 'maybe': 22, 'someday': 20, 'better': 18, 'hold': 18
    }
}

PHRASE_RULES = [
    (r'\btired of everything\b|\bdone with everything\b', {'Burnout': 54, 'Hopelessness': 34, 'Mental Fatigue': 38, 'Quiet Sadness': 18}),
    (r"\bi don'?t feel okay\b.*\bdon'?t want to talk\b|\bdon'?t want to talk\b.*\bi don'?t feel okay\b", {'Emotional Suppression': 62, 'Loneliness': 26, 'Mental Fatigue': 24, 'Quiet Sadness': 30}),
    (r"\bpretending i'?m fine\b|\bpretend i'?m okay\b|\bbottle it up\b", {'Emotional Suppression': 54, 'Quiet Sadness': 28, 'Loneliness': 18}),
    (r'\btrying to stay calm\b|\btrying to be calm\b', {'Quiet Healing': 36, 'Calmness': 28, 'Burnout': 12}),
    (r'\bi feel nothing\b|\bcan\'?t feel anything\b|\bemotionally numb\b', {'Emotional Numbness': 58, 'Existential Emptiness': 26, 'Melancholy': 18}),
    (r'\blate[- ]night overthinking\b|\boverthinking at night\b', {'Late Night Overthinking': 58, 'Anxiety': 26, 'Introspection': 28}),
    (r'\bgrief with acceptance\b|\baccepting the loss\b', {'Grief Acceptance': 58, 'Sadness': 24, 'Serenity': 22}),
    (r'\bquiet healing\b', {'Quiet Healing': 58, 'Hopefulness': 24, 'Serenity': 20}),
    (r'\bwatching the rain\b', {'Melancholy': 34, 'Calmness': 28, 'Introspection': 28, 'Serenity': 12}),
    (r'\brain (hit|hits|hitting) the window\b', {'Melancholy': 40, 'Introspection': 34, 'Calmness': 30, 'Nostalgia': 16}),
    (r'\bmiss (her|him|them|you)\b', {'Sadness': 34, 'Loneliness': 30, 'Nostalgia': 26, 'Romantic Warmth': 16}),
    (r"\bi'?ll be okay\b|\bi will be okay\b", {'Hopefulness': 42, 'Sadness': 10, 'Serenity': 16}),
    (r'\bunstoppable tonight\b', {'Confidence': 46, 'Energy': 34, 'Excitement': 28, 'Motivation': 28}),
    (r'\bcan\'?t sleep\b|\bsleepless\b', {'Anxiety': 28, 'Introspection': 24, 'Melancholy': 16}),
    (r'\bdeep work\b|\bblock the noise\b', {'Motivation': 32, 'Introspection': 24, 'Calmness': 18}),
    (r'\blong day\b', {'Sadness': 12, 'Calmness': 14, 'Serenity': 10}),
    (r'\bfeel empty\b|\bempty after getting rejected\b|\bafter getting rejected\b', {'Emotional Numbness': 58, 'Hopelessness': 26, 'Loneliness': 24, 'Sadness': 18}),
    (r'\bcan\'?t sleep\b|\bcannot sleep\b|\bsleepless\b', {'Late Night Overthinking': 54, 'Anxiety': 24, 'Introspection': 18}),
    (r'\bpeaceful\b|\bpeace\b', {'Calmness': 28, 'Serenity': 24, 'Introspection': 10}),
    (r'\bneed confidence\b|\bconfident now\b|\bneed to feel confident\b', {'Confidence': 44, 'Euphoric Confidence': 20, 'Motivation': 16}),
    (r'\bjust got promoted\b|\bpromoted\b', {'Confidence': 36, 'Euphoric Confidence': 22, 'Hopefulness': 16}),
    (r'\bdriving alone\b|\bdrive alone\b', {'Nostalgia': 24, 'Loneliness': 22, 'Introspection': 20, 'Calmness': 10}),
    (r'\bi want to cry\b|\bwant to cry\b', {'Sadness': 32, 'Hopelessness': 16, 'Loneliness': 16, 'Quiet Sadness': 18}),
]

CONTEXT_PATTERNS = {
    'time': {
        'morning': r'\bmorning\b',
        'afternoon': r'\bafternoon\b',
        'evening': r'\bevening\b',
        'night': r'\bnight\b|\bmidnight\b|\blate\b|\b2am\b|\b3am\b',
    },
    'weather': {
        'rain': r'\brain\b|\brainy\b|\bdrizzle\b|\bpouring\b',
        'storm': r'\bstorm\b|\bthunder\b',
        'cloudy': r'\bcloudy\b|\bgrey\b|\bgray\b',
        'sunny': r'\bsunny\b|\bsun\b',
    },
    'activity': {
        'working': r'\bwork\b|\bworking\b|\bcoding\b|\bstudying\b|\bfocus\b',
        'moving': r'\brunning\b|\bgym\b|\bdance\b|\bmove\b',
        'resting': r'\brest\b|\bresting\b|\bsleep\b|\bwatching\b',
        'social': r'\bfriends\b|\bparty\b|\bclub\b|\bdate\b',
    }
}

MOOD_PROFILES = {
    'Burnout': {'Burnout': 0.42, 'Mental Fatigue': 0.28, 'Hopelessness': 0.16, 'Calmness': 0.14},
    'Numb': {'Emotional Numbness': 0.48, 'Existential Emptiness': 0.26, 'Melancholy': 0.16, 'Introspection': 0.10},
    'Healing': {'Quiet Healing': 0.42, 'Hopefulness': 0.22, 'Serenity': 0.20, 'Sadness': 0.16},
    'Suppressed': {'Emotional Suppression': 0.46, 'Quiet Sadness': 0.24, 'Loneliness': 0.18, 'Mental Fatigue': 0.12},
    'Happy': {'Hopefulness': 0.4, 'Excitement': 0.28, 'Confidence': 0.16, 'Energy': 0.16},
    'Sad': {'Sadness': 0.38, 'Melancholy': 0.22, 'Loneliness': 0.18, 'Nostalgia': 0.14, 'Introspection': 0.08},
    'Angry': {'Anger': 0.58, 'Energy': 0.2, 'Anxiety': 0.14, 'Confidence': 0.08},
    'Chill': {'Calmness': 0.36, 'Serenity': 0.28, 'Introspection': 0.16, 'Melancholy': 0.12, 'Hopefulness': 0.08},
    'Romantic': {'Romantic Warmth': 0.38, 'Nostalgia': 0.18, 'Hopefulness': 0.16, 'Calmness': 0.14, 'Sadness': 0.14},
    'Motivated': {'Motivation': 0.38, 'Confidence': 0.28, 'Energy': 0.2, 'Excitement': 0.14},
    'Lonely': {'Loneliness': 0.42, 'Sadness': 0.22, 'Melancholy': 0.18, 'Introspection': 0.18},
    'Energetic': {'Energy': 0.36, 'Excitement': 0.3, 'Confidence': 0.18, 'Motivation': 0.16},
    'Focus': {'Motivation': 0.3, 'Introspection': 0.28, 'Calmness': 0.22, 'Serenity': 0.2},
    'Late Night': {'Melancholy': 0.26, 'Introspection': 0.24, 'Calmness': 0.2, 'Loneliness': 0.16, 'Nostalgia': 0.14},
    'Rainy': {'Melancholy': 0.28, 'Calmness': 0.24, 'Introspection': 0.22, 'Nostalgia': 0.14, 'Loneliness': 0.12},
    'Party': {'Excitement': 0.36, 'Energy': 0.34, 'Confidence': 0.16, 'Hopefulness': 0.14},
}


def _clamp(value, low=0, high=100):
    return max(low, min(high, value))


def _has_word(text, word):
    return re.search(rf'\b{re.escape(word)}\b', text) is not None


def _extract_context(text):
    context = {'time': None, 'weather': None, 'activity': None}
    for category, patterns in CONTEXT_PATTERNS.items():
        for value, pattern in patterns.items():
            if re.search(pattern, text):
                context[category] = value
                break
    return context


def _apply_lexicon(scores, text):
    tokens = re.findall(r"[a-z']+", text)
    token_set = set(tokens)
    hits = []
    for emotion, words in EMOTION_LEXICON.items():
        for word, weight in words.items():
            if word in token_set or _has_word(text, word):
                scores[emotion] += weight
                hits.append(word)
    for pattern, boosts in PHRASE_RULES:
        if re.search(pattern, text):
            for emotion, weight in boosts.items():
                scores[emotion] += weight
    return hits


def _apply_sentiment(scores, vader, polarity):
    compound = vader['compound']
    if compound < -0.18:
        scores['Sadness'] += abs(compound) * 34
        scores['Melancholy'] += abs(compound) * 18
    if compound > 0.18:
        scores['Hopefulness'] += compound * 30
        scores['Excitement'] += compound * 18
    if vader['neg'] > 0.18:
        scores['Sadness'] += vader['neg'] * 34
        scores['Anxiety'] += vader['neg'] * 14
    if vader['pos'] > 0.18:
        scores['Confidence'] += vader['pos'] * 18
        scores['Hopefulness'] += vader['pos'] * 22
    if polarity < -0.12:
        scores['Sadness'] += abs(polarity) * 18
    if polarity > 0.12:
        scores['Hopefulness'] += polarity * 16


def _apply_context(scores, context, text):
    if context['weather'] == 'rain':
        scores['Melancholy'] += 26
        scores['Calmness'] += 20
        scores['Introspection'] += 18
        scores['Anger'] *= 0.35
        scores['Energy'] *= 0.55
    if context['weather'] == 'storm':
        scores['Anxiety'] += 18
        scores['Melancholy'] += 12
        scores['Energy'] += 8
    if context['time'] == 'night':
        scores['Introspection'] += 14
        scores['Melancholy'] += 12
        scores['Excitement'] += 8 if re.search(r'\btonight\b|\bparty\b|\bclub\b', text) else 0
    if context['activity'] == 'working':
        scores['Motivation'] += 20
        scores['Introspection'] += 14
        scores['Calmness'] += 8
    if context['activity'] == 'moving':
        scores['Energy'] += 22
        scores['Excitement'] += 14
    if context['activity'] == 'social':
        scores['Excitement'] += 18
        scores['Romantic Warmth'] += 12 if re.search(r'\bdate\b|\blove\b|\bher\b|\bhim\b', text) else 0


def _apply_contrast_rules(scores, text):
    if re.search(r'\bbut\b|\balthough\b|\bhowever\b', text):
        scores['Introspection'] += 12
    if re.search(r"\bdon'?t want to talk\b|\bnot ready to talk\b|\bpretending i'?m fine\b", text):
        scores['Emotional Suppression'] += 34
        scores['Quiet Sadness'] += 18
        scores['Loneliness'] += 12
    if re.search(r'\btired of everything\b', text) and re.search(r'\bcalm\b|\btrying\b|\bbreathe\b', text):
        scores['Burnout'] += 34
        scores['Mental Fatigue'] += 22
        scores['Calmness'] += 16
        scores['Hopelessness'] += 14
        scores['Sadness'] *= 0.72
    if re.search(r'\bnumb\b|\bfeel nothing\b|\bempty\b', text):
        scores['Emotional Numbness'] += 24
        scores['Energy'] *= 0.55
        scores['Excitement'] *= 0.45
    if re.search(r'\baccept\b|\bacceptance\b', text) and re.search(r'\bgrief\b|\bloss\b|\blost\b|\bgoodbye\b', text):
        scores['Grief Acceptance'] += 30
        scores['Serenity'] += 14
    if re.search(r"\bmiss\b", text) and re.search(r"\bokay\b|\bhope\b|\bheal", text):
        scores['Hopefulness'] += 18
        scores['Nostalgia'] += 12
    if scores['Calmness'] + scores['Melancholy'] + scores['Introspection'] > 85:
        scores['Anger'] *= 0.15
        scores['Energy'] *= 0.5
        scores['Excitement'] *= 0.45
    if scores['Anger'] < 18 and not re.search(r'\bangry\b|\bmad\b|\bhate\b|\bfurious\b|\brage\b', text):
        scores['Anger'] = 0


def _dimensions(scores, vader):
    positive = scores['Hopefulness'] + scores['Excitement'] + scores['Confidence'] + scores['Romantic Warmth']
    negative = scores['Sadness'] + scores['Melancholy'] + scores['Loneliness'] + scores['Anxiety'] + scores['Anger']
    valence_score = _clamp(50 + (positive - negative) * 0.42 + vader['compound'] * 24)
    energy = _clamp(scores['Energy'] * 0.72 + scores['Excitement'] * 0.36 + scores['Anger'] * 0.22 + scores['Calmness'] * -0.18 + 24)
    introspection = _clamp(scores['Introspection'] * 0.72 + scores['Melancholy'] * 0.32 + scores['Nostalgia'] * 0.24 + 18)
    emotional_depth = _clamp(scores['Sadness'] * 0.42 + scores['Melancholy'] * 0.48 + scores['Nostalgia'] * 0.38 + scores['Romantic Warmth'] * 0.18 + 20)
    social_warmth = _clamp(scores['Romantic Warmth'] * 0.52 + scores['Hopefulness'] * 0.24 + scores['Loneliness'] * -0.16 + 34)
    mental_intensity = _clamp(scores['Anxiety'] * 0.34 + scores['Motivation'] * 0.28 + scores['Introspection'] * 0.32 + scores['Confidence'] * 0.18 + 24)
    if valence_score < 35:
        valence = 'low'
    elif valence_score < 48:
        valence = 'low-positive'
    elif valence_score < 62:
        valence = 'balanced'
    else:
        valence = 'positive'
    return {
        'valence': valence,
        'valenceScore': round(valence_score),
        'energy': round(energy),
        'introspection': round(introspection),
        'emotionalDepth': round(emotional_depth),
        'socialWarmth': round(social_warmth),
        'mentalIntensity': round(mental_intensity)
    }


def _normalize_scores(raw_scores):
    active = {k: _clamp(v) for k, v in raw_scores.items() if v >= 8}
    if not active:
        active = {'Calmness': 42, 'Introspection': 18, 'Serenity': 16}
    top = sorted(active.items(), key=lambda item: item[1], reverse=True)[:6]
    total = sum(value for _, value in top) or 1
    normalized = {label: round((value / total) * 100, 1) for label, value in top}
    drift = round(100 - sum(normalized.values()), 1)
    if normalized and abs(drift) >= 0.1:
        first = next(iter(normalized))
        normalized[first] = round(normalized[first] + drift, 1)
    return normalized


def _profile_strength(scores, profile):
    return sum(scores.get(emotion, 0) * weight for emotion, weight in profile.items())


def _select_mood(raw_scores, context):
    profile_scores = {mood: _profile_strength(raw_scores, profile) for mood, profile in MOOD_PROFILES.items()}
    if context['weather'] == 'rain':
        profile_scores['Rainy'] += 20
        profile_scores['Chill'] += 8
    if context['time'] == 'night':
        profile_scores['Late Night'] += 12
    if raw_scores.get('Emotional Suppression', 0) + raw_scores.get('Quiet Sadness', 0) > 48:
        profile_scores['Suppressed'] += 38
        profile_scores['Sad'] *= 0.82
    if raw_scores.get('Burnout', 0) + raw_scores.get('Mental Fatigue', 0) > 58:
        profile_scores['Burnout'] += 36
        profile_scores['Sad'] *= 0.78
    if raw_scores.get('Emotional Numbness', 0) + raw_scores.get('Existential Emptiness', 0) > 54:
        profile_scores['Numb'] += 34
        profile_scores['Late Night'] += 10
    if raw_scores.get('Quiet Healing', 0) + raw_scores.get('Grief Acceptance', 0) > 48:
        profile_scores['Healing'] += 32
    if raw_scores['Confidence'] + raw_scores['Motivation'] + raw_scores.get('Euphoric Confidence', 0) > 70:
        profile_scores['Motivated'] += 18
    if raw_scores['Energy'] + raw_scores['Excitement'] > 75:
        profile_scores['Energetic'] += 16
    if raw_scores['Romantic Warmth'] > 45:
        profile_scores['Romantic'] += 18
    if raw_scores['Sadness'] + raw_scores['Hopefulness'] + raw_scores['Nostalgia'] > raw_scores['Romantic Warmth'] * 2.2:
        profile_scores['Sad'] += 18
        profile_scores['Romantic'] *= 0.78
    return max(profile_scores.items(), key=lambda item: item[1])[0]


def _intensity(raw_scores, dimensions):
    peak = max(raw_scores.values()) if raw_scores else 0
    depth = dimensions['emotionalDepth']
    mental = dimensions['mentalIntensity']
    if peak > 92 or max(depth, mental) > 86:
        return 'extreme'
    if peak > 66 or max(depth, mental) > 66:
        return 'high'
    if peak > 34 or max(depth, mental) > 42:
        return 'moderate'
    return 'low'


def _archetype(primary, secondary, dimensions, context):
    if primary == 'Burnout':
        return 'Emotional Burnout'
    if primary == 'Mental Fatigue':
        return 'Cognitive Exhaustion'
    if primary == 'Emotional Numbness':
        return 'Soft Numbness'
    if primary == 'Existential Emptiness':
        return 'Existential Drift'
    if primary == 'Late Night Overthinking':
        return 'Late Night Overthinking'
    if primary == 'Quiet Healing':
        return 'Quiet Healing'
    if primary == 'Grief Acceptance':
        return 'Grief with Acceptance'
    if primary == 'Euphoric Confidence':
        return 'Euphoric Confidence'
    if primary == 'Melancholy' and dimensions['introspection'] > 65 and context.get('weather') == 'rain':
        return 'Rainlit Reflection'
    if primary == 'Loneliness' and context.get('time') == 'night':
        return 'Neon Loneliness'
    if {primary, secondary} == {'Sadness', 'Hopefulness'}:
        return 'Quiet Healing'
    if primary == 'Confidence' and secondary in ['Energy', 'Excitement', 'Motivation']:
        return 'Stormy Euphoria'
    if primary == 'Nostalgia' and dimensions['valenceScore'] >= 42:
        return 'Golden Nostalgia'
    if primary == 'Calmness' and secondary == 'Introspection':
        return 'Midnight Reflection' if context.get('time') == 'night' else 'Soft Stillness'
    if primary == 'Anxiety' and secondary == 'Calmness':
        return 'Soft Chaos'
    return f"{primary} {secondary}" if secondary else primary


def _nuance_label(primary, secondary, dimensions, context):
    if primary == 'Burnout':
        return 'Burnout under Control' if secondary in ['Calmness', 'Quiet Healing'] else 'Emotional Burnout'
    if primary == 'Mental Fatigue':
        return 'Mental Fatigue'
    if primary == 'Hopelessness':
        return 'Quiet Hopelessness'
    if primary == 'Emotional Numbness':
        return 'Emotional Numbness'
    if primary == 'Existential Emptiness':
        return 'Existential Emptiness'
    if primary == 'Late Night Overthinking':
        return 'Late-night Overthinking'
    if primary == 'Quiet Healing':
        return 'Quiet Healing'
    if primary == 'Grief Acceptance':
        return 'Grief with Acceptance'
    if primary == 'Euphoric Confidence':
        return 'Euphoric Confidence'
    if primary == 'Melancholy' and secondary in ['Calmness', 'Introspection']:
        return 'Melancholic Calm'
    if {primary, secondary} == {'Sadness', 'Hopefulness'}:
        return 'Sad but Hopeful'
    if primary == 'Confidence' and secondary in ['Energy', 'Motivation', 'Excitement']:
        return 'Confident Momentum'
    if primary == 'Loneliness' and secondary == 'Nostalgia':
        return 'Lonely Nostalgia'
    if primary == 'Romantic Warmth' and secondary in ['Sadness', 'Nostalgia']:
        return 'Tender Longing'
    if dimensions['introspection'] > 75 and primary in ['Calmness', 'Melancholy']:
        return 'Deep Reflective Calm'
    if secondary:
        return f"{primary} with {secondary}"
    return primary


def analyze_text(text):
    if not text:
        return {
            'mood': 'Chill',
            'secondary': None,
            'nuancedLabel': 'Neutral & Calm',
            'archetype': 'Soft Stillness',
            'intensity': 'low',
            'scores': {'Calmness': 100},
            'dimensions': {'valence': 'balanced', 'valenceScore': 50, 'energy': 20, 'introspection': 30, 'emotionalDepth': 20, 'socialWarmth': 40, 'mentalIntensity': 20},
            'confidence': 0.45,
            'context': {'time': None, 'weather': None, 'activity': None},
            'keywords': []
        }

    clean_text = text.lower().strip()
    vader = analyzer.polarity_scores(text)
    try:
        polarity = TextBlob(text).sentiment.polarity
    except Exception:
        polarity = 0

    raw_scores = {emotion: 0.0 for emotion in EMOTIONS}
    raw_scores['Calmness'] = 8
    raw_scores['Introspection'] = 6
    raw_scores['Serenity'] = 4

    context = _extract_context(clean_text)
    hits = _apply_lexicon(raw_scores, clean_text)
    _apply_sentiment(raw_scores, vader, polarity)
    _apply_context(raw_scores, context, clean_text)
    _apply_contrast_rules(raw_scores, clean_text)

    raw_scores = {emotion: _clamp(score) for emotion, score in raw_scores.items()}
    dimensions = _dimensions(raw_scores, vader)
    normalized_scores = _normalize_scores(raw_scores)
    ranked = sorted(normalized_scores.items(), key=lambda item: item[1], reverse=True)

    primary_emotion = ranked[0][0]
    if context['weather'] == 'rain' and normalized_scores.get('Melancholy', 0) >= ranked[0][1] - 4:
        primary_emotion = 'Melancholy'
        ranked = [('Melancholy', normalized_scores['Melancholy'])] + [item for item in ranked if item[0] != 'Melancholy']
    secondary_emotion = ranked[1][0] if len(ranked) > 1 and ranked[1][1] >= 12 else None
    hidden_undertone = ranked[2][0] if len(ranked) > 2 and ranked[2][1] >= 8 else None
    mood = _select_mood(raw_scores, context)
    intensity = _intensity(raw_scores, dimensions)
    archetype = _archetype(primary_emotion, secondary_emotion, dimensions, context)
    nuanced_label = _nuance_label(primary_emotion, secondary_emotion, dimensions, context)

    evidence = min(len(set(hits)), 8)
    spread = ranked[0][1] - (ranked[1][1] if len(ranked) > 1 else 0)
    confidence = _clamp(58 + evidence * 4 + spread * 0.35 + abs(vader['compound']) * 12, 54, 94)

    return {
        'mood': mood,
        'primaryEmotion': primary_emotion,
        'secondary': secondary_emotion,
        'hiddenUndertone': hidden_undertone,
        'nuancedLabel': nuanced_label,
        'archetype': archetype,
        'intensity': intensity,
        'scores': normalized_scores,
        'dimensions': dimensions,
        'confidence': round(confidence / 100, 2),
        'context': context,
        'keywords': sorted(set(hits))[:10]
    }
