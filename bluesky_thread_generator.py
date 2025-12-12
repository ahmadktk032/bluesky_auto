"""
Bluesky AI Thread Generator
Creates engaging thread posts optimized for Bluesky
Uses: Groq, Gemini APIs
"""

import requests
import time
from typing import Optional, Dict, List


class BlueskyThreadGenerator:
    """Generate engaging threads for Bluesky"""
    
    def __init__(self, providers: Dict[str, str]):
        """
        Initialize generator
        
        Args:
            providers: Dict with 'groq' and/or 'gemini' API keys
        """
        self.providers = providers
        self.provider_list = list(providers.keys())
        self.current_index = 0
        
        self.configs = {
            'groq': {
                'url': 'https://api.groq.com/openai/v1/chat/completions',
                'model': 'llama-3.3-70b-versatile'
            },
            'gemini': {
                'url': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent',
                'model': 'gemini-1.5-flash'
            }
        }
        
        print(f"✓ Bluesky Thread Generator initialized")
        print(f"  Providers: {', '.join(self.provider_list)}")
    
    def _create_thread_prompt(self, topic: str) -> str:
        """Create prompt for thread generation"""
        
        prompt = f"""Create an engaging Bluesky thread about: "{topic}"

**BLUESKY THREAD REQUIREMENTS:**

1. **Thread Structure (5-7 posts):**
   - Post 1: Hook that grabs attention (question, bold claim, story opener)
   - Posts 2-5: Valuable content, insights, tips, or story progression
   - Post 6-7: Strong conclusion + engagement question

2. **Each Post Must:**
   - Be 200-280 characters (Bluesky limit: 300, but 200-280 is optimal)
   - Start strong (no filler words like "so", "well", "just")
   - Use line breaks for readability
   - Feel conversational and authentic
   - Be self-contained (make sense if read alone)

3. **Engagement Tactics:**
   - Use numbers and specifics ("saved $847" vs "saved money")
   - Share personal experience or lessons learned
   - Create curiosity gaps ("Here's what happened next...")
   - Ask questions to spark replies
   - Use power words (proven, mistake, secret, transform, realized)
   - Add vulnerability (makes it relatable)

4. **Bluesky Culture:**
   - More conversational than Twitter
   - Less corporate, more authentic
   - Community-focused (not just broadcasting)
   - Thoughtful and substantive (not just hot takes)
   - Supportive tone (Bluesky users value kindness)

5. **Format:**
   - Number each post (1/7, 2/7, etc.)
   - No hashtags (Bluesky doesn't use them much)
   - Emojis okay if natural (1-2 per post max)
   - Use @ mentions sparingly

6. **Content Quality:**
   - Teach something useful
   - Share genuine insights
   - Be specific with examples
   - Show your personality
   - Value > promotion

**OUTPUT FORMAT:**
Return each post separated by "---"

Example:
Post 1 text here (1/5)
---
Post 2 text here (2/5)
---
etc.

Write the thread now (5-7 posts):"""
        
        return prompt
    
    def _call_groq(self, prompt: str) -> Optional[str]:
        """Call Groq API"""
        headers = {
            'Authorization': f'Bearer {self.providers["groq"]}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.configs['groq']['model'],
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a Bluesky content expert. You understand that Bluesky users value authentic, thoughtful, and substantive content. You create threads that spark genuine conversations and provide real value.'
                },
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.8,
            'max_tokens': 1000
        }
        
        try:
            response = requests.post(
                self.configs['groq']['url'],
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                print(f"  ❌ Groq error: {response.status_code}")
                return None
        except Exception as e:
            print(f"  ❌ Groq exception: {e}")
            return None
    
    def _call_gemini(self, prompt: str) -> Optional[str]:
        """Call Gemini API"""
        url = f"{self.configs['gemini']['url']}?key={self.providers['gemini']}"
        
        payload = {
            'contents': [{'parts': [{'text': prompt}]}],
            'generationConfig': {'temperature': 0.8, 'maxOutputTokens': 1000}
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f"  ❌ Gemini error: {response.status_code}")
                return None
        except Exception as e:
            print(f"  ❌ Gemini exception: {e}")
            return None
    
    def generate_thread(self, topic: str, retry_count: int = 2) -> Optional[List[str]]:
        """
        Generate thread posts
        
        Args:
            topic: Thread topic
            retry_count: Number of providers to try
        
        Returns:
            List of post texts or None
        """
        print(f"\n🦋 Generating thread: {topic}")
        
        prompt = self._create_thread_prompt(topic)
        
        attempts = 0
        while attempts < retry_count and attempts < len(self.provider_list):
            provider = self.provider_list[self.current_index]
            print(f"   Using: {provider.upper()}")
            
            if provider == 'groq':
                content = self._call_groq(prompt)
            elif provider == 'gemini':
                content = self._call_gemini(prompt)
            else:
                content = None
            
            if content:
                posts = self._parse_thread(content)
                if posts and len(posts) >= 3:
                    print(f"   ✓ Thread generated: {len(posts)} posts")
                    return posts
            
            self.current_index = (self.current_index + 1) % len(self.provider_list)
            attempts += 1
            time.sleep(1)
        
        print(f"   ❌ Failed to generate thread")
        return None
    
    def _parse_thread(self, content: str) -> List[str]:
        """Parse thread into individual posts"""
        # Remove AI prefixes
        prefixes = ["Here's the thread:", "Here are the posts:", "Thread:"]
        for prefix in prefixes:
            if content.lower().startswith(prefix.lower()):
                content = content[len(prefix):].strip()
        
        # Split by separator
        if '---' in content:
            posts = content.split('---')
        elif '\n\n\n' in content:
            posts = content.split('\n\n\n')
        else:
            # Split by post numbers
            import re
            parts = re.split(r'\n\s*\d+/\d+\s*\n', content)
            posts = [p.strip() for p in parts if p.strip()]
        
        # Clean posts
        cleaned = []
        for post in posts:
            post = post.strip()
            # Remove quotes
            if post.startswith('"') and post.endswith('"'):
                post = post[1:-1]
            # Validate length (Bluesky max: 300 chars)
            if post and len(post) <= 300:
                cleaned.append(post)
        
        return cleaned
    
    def generate_batch(self, topics: List[str]) -> List[Dict]:
        """Generate multiple threads"""
        results = []
        
        print(f"\n{'='*70}")
        print(f"BATCH THREAD GENERATION")
        print(f"Total threads: {len(topics)}")
        print(f"{'='*70}")
        
        for idx, topic in enumerate(topics, 1):
            print(f"\n[{idx}/{len(topics)}] ━━━━━━━━━━━━━━━━━━━━━━━")
            
            posts = self.generate_thread(topic)
            
            results.append({
                'topic': topic,
                'posts': posts,
                'status': 'success' if posts else 'failed'
            })
            
            if idx < len(topics):
                time.sleep(2)
        
        success = sum(1 for r in results if r['status'] == 'success')
        print(f"\n{'='*70}")
        print(f"COMPLETE: {success}/{len(topics)} successful")
        print(f"{'='*70}\n")
        
        return results