"""
Bluesky Publisher
Posts threads to Bluesky using AT Protocol
"""

import requests
import time
from typing import Optional, Dict, List
from datetime import datetime, timezone


class BlueskyPublisher:
    """Publish threads to Bluesky"""
    
    def __init__(self, handle: str, app_password: str):
        """
        Initialize Bluesky publisher
        
        Args:
            handle: Your Bluesky handle (e.g., "username.bsky.social")
            app_password: App-specific password from settings
        """
        self.handle = handle
        self.app_password = app_password
        self.session = None
        self.did = None
        
        # Bluesky API endpoint
        self.api_url = "https://bsky.social/xrpc"
        
        # Authenticate
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Bluesky"""
        url = f"{self.api_url}/com.atproto.server.createSession"
        
        payload = {
            "identifier": self.handle,
            "password": self.app_password
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.session = data
                self.did = data['did']
                print(f"✓ Authenticated as {self.handle}")
                return True
            else:
                print(f"❌ Auth failed: {response.status_code}")
                print(f"   {response.text}")
                return False
        except Exception as e:
            print(f"❌ Auth exception: {e}")
            return False
    
    def _get_headers(self) -> Dict:
        """Get request headers with auth token"""
        return {
            'Authorization': f'Bearer {self.session["accessJwt"]}',
            'Content-Type': 'application/json'
        }
    
    def create_post(self, text: str, reply_to: Optional[Dict] = None,
                   image_blob: Optional[Dict] = None) -> Optional[Dict]:
        """
        Create a post
        
        Args:
            text: Post text (max 300 chars)
            reply_to: Reply reference for threading
            image_blob: Uploaded image blob reference
        
        Returns:
            Post data or None
        """
        url = f"{self.api_url}/com.atproto.repo.createRecord"
        
        # Build post record
        record = {
            '$type': 'app.bsky.feed.post',
            'text': text,
            'createdAt': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        
        # Add reply reference for threading
        if reply_to:
            record['reply'] = reply_to
        
        # Add image if provided
        if image_blob:
            record['embed'] = {
                '$type': 'app.bsky.embed.images',
                'images': [{
                    'alt': '',
                    'image': image_blob
                }]
            }
        
        payload = {
            'repo': self.did,
            'collection': 'app.bsky.feed.post',
            'record': record
        }
        
        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'uri': data['uri'],
                    'cid': data['cid']
                }
            else:
                print(f"  ❌ Post failed: {response.status_code}")
                print(f"     {response.text[:200]}")
                return None
        except Exception as e:
            print(f"  ❌ Exception: {e}")
            return None
    
    def post_thread(self, posts: List[str], image_path: Optional[str] = None) -> Optional[List[Dict]]:
        """
        Post a thread
        
        Args:
            posts: List of post texts
            image_path: Optional image for first post
        
        Returns:
            List of posted data or None
        """
        if not posts or len(posts) < 1:
            print("❌ No posts to publish")
            return None
        
        print(f"\n📤 Posting thread ({len(posts)} posts)...")
        
        posted = []
        reply_ref = None
        
        # Upload image if provided (for first post)
        image_blob = None
        if image_path:
            image_blob = self.upload_image(image_path)
        
        for idx, text in enumerate(posts, 1):
            print(f"\n  Post {idx}/{len(posts)}")
            print(f"  Text: {text[:60]}...")
            
            # Only add image to first post
            img = image_blob if idx == 1 else None
            
            result = self.create_post(text, reply_to=reply_ref, image_blob=img)
            
            if result:
                posted.append(result)
                print(f"  ✓ Posted")
                
                # Create reply reference for next post
                reply_ref = {
                    'root': {
                        'uri': posted[0]['uri'],
                        'cid': posted[0]['cid']
                    },
                    'parent': {
                        'uri': result['uri'],
                        'cid': result['cid']
                    }
                }
                
                # Small delay between posts
                if idx < len(posts):
                    time.sleep(2)
            else:
                print(f"  ❌ Failed, stopping thread")
                break
        
        if len(posted) == len(posts):
            # Extract post ID from URI
            post_id = posted[0]['uri'].split('/')[-1]
            print(f"\n✓ Thread posted successfully!")
            print(f"  View: https://bsky.app/profile/{self.handle}/post/{post_id}")
            return posted
        else:
            print(f"\n⚠️  Partial thread: {len(posted)}/{len(posts)}")
            return posted if posted else None
    
    def upload_image(self, image_path: str) -> Optional[Dict]:
        """
        Upload image to Bluesky
        
        Args:
            image_path: Path to image file
        
        Returns:
            Blob reference or None
        """
        import os
        
        if not os.path.exists(image_path):
            print(f"  ⚠️  Image not found: {image_path}")
            return None
        
        url = f"{self.api_url}/com.atproto.repo.uploadBlob"
        
        try:
            # Detect mimetype
            ext = os.path.splitext(image_path)[1].lower()
            mimetypes = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            mimetype = mimetypes.get(ext, 'image/jpeg')
            
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            headers = {
                'Authorization': f'Bearer {self.session["accessJwt"]}',
                'Content-Type': mimetype
            }
            
            response = requests.post(url, headers=headers, data=image_data)
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Image uploaded")
                return data['blob']
            else:
                print(f"  ❌ Upload failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"  ❌ Upload exception: {e}")
            return None