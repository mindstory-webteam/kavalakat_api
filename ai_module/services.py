import json, re, logging
from django.conf import settings
logger = logging.getLogger('ai_module')

def generate_blog_content(topic: str) -> dict:
    api_key = getattr(settings,'OPENAI_API_KEY','').strip()
    if not api_key: raise ValueError('OPENAI_API_KEY is not configured.')
    try:
        from openai import OpenAI
    except ImportError:
        raise ValueError('openai package not installed. Run: pip install openai')
    client = OpenAI(api_key=api_key)
    model  = 'gpt-4o-mini'
    prompt = f"""Write a comprehensive SEO-optimised blog post about: {topic}
Return ONLY valid JSON (no markdown fences) with keys:
title, excerpt, content (markdown 600-900 words with ## subheadings), tags, meta_title, meta_description"""
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {'role':'system','content':'You are a cement industry content expert. Return raw JSON only.'},
                {'role':'user','content':prompt}
            ],
            temperature=0.75, max_tokens=1800
        )
    except Exception as exc:
        logger.error('OpenAI error: %s', exc)
        raise RuntimeError(f'OpenAI API error: {exc}') from exc
    raw    = resp.choices[0].message.content.strip()
    tokens = resp.usage.total_tokens if resp.usage else 0
    clean  = re.sub(r'^```(?:json)?\s*','',raw); clean = re.sub(r'\s*```$','',clean.strip())
    try:
        data = json.loads(clean)
    except json.JSONDecodeError:
        m = re.search(r'\{.*\}', clean, re.DOTALL)
        if m:
            try: data = json.loads(m.group())
            except: raise RuntimeError('OpenAI returned malformed JSON.')
        else: raise RuntimeError('OpenAI returned malformed JSON.')
    missing = {'title','excerpt','content'} - set(data.keys())
    if missing: raise RuntimeError(f'OpenAI response missing: {missing}')
    return {
        'title': data['title'].strip(), 'excerpt': data['excerpt'].strip(),
        'content': data['content'].strip(), 'tags': data.get('tags','').strip(),
        'meta_title': data.get('meta_title','').strip(),
        'meta_description': data.get('meta_description','').strip(),
        'model_used': model, 'tokens_used': tokens,
    }
