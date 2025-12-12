"""
Complete Bluesky Automation System
Posts 3 engaging threads per day
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import time

from bluesky_thread_generator import BlueskyThreadGenerator
from bluesky_publisher import BlueskyPublisher


class BlueskyAutomation:
    """Main automation system"""
    
    def __init__(self, config_file: str = 'bluesky_config.json', schedule_file: str = 'BLUESKY_SCHEDULE.json'):
        """Initialize automation system"""
        self.config_file = config_file
        self.schedule_file = schedule_file
        self.config = self.load_config()
        self.schedule = self.load_schedule()
        
        # Initialize AI generator
        self.generator = BlueskyThreadGenerator(self.config['ai_providers'])
        
        # Initialize Bluesky publisher
        bsky = self.config['bluesky']
        self.publisher = BlueskyPublisher(bsky['handle'], bsky['app_password'])
        
        print("\n" + "="*70)
        print("BLUESKY AUTOMATION INITIALIZED")
        print("="*70)
        print(f"✓ AI Generator ready")
        print(f"✓ Bluesky authenticated: {bsky['handle']}")
        print(f"✓ Schedule: {len(self.schedule)} days")
        print("="*70 + "\n")
    
    def load_config(self) -> Dict:
        """Load configuration"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"❌ Config not found: {self.config_file}")
            self.create_sample_config()
            raise FileNotFoundError("Please edit config and run again")
    
    def load_schedule(self) -> List[Dict]:
        """Load schedule from separate file"""
        if os.path.exists(self.schedule_file):
            with open(self.schedule_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Handle both direct list and wrapped in 'schedule' key
                return data.get('schedule', data) if isinstance(data, dict) else data
        else:
            print(f"❌ Schedule not found: {self.schedule_file}")
            raise FileNotFoundError(f"Please create {self.schedule_file}")
    
    def create_sample_config(self):
        """Create sample configuration"""
        config = {
            "_comment": "Bluesky Automation Configuration",
            
            "ai_providers": {
                "groq": "your-groq-api-key-here",
                "gemini": "your-gemini-api-key-here"
            },
            
            "bluesky": {
                "handle": "username.bsky.social",
                "app_password": "xxxx-xxxx-xxxx-xxxx"
            },
            
            "posting_times": ["09:00", "14:00", "19:00"],
            
            "schedule": [
                {
                    "day": 1,
                    "date": "2025-12-09",
                    "threads": [
                        {
                            "time": "09:00",
                            "topic": "Why I switched from Twitter to Bluesky",
                            "image": "images/day1_morning.jpg"
                        },
                        {
                            "time": "14:00",
                            "topic": "5 productivity lessons from building in public",
                            "image": null
                        },
                        {
                            "time": "19:00",
                            "topic": "The mindset shift that changed my career",
                            "image": "images/day1_evening.jpg"
                        }
                    ]
                },
                {
                    "day": 2,
                    "date": "2025-12-10",
                    "threads": [
                        {
                            "time": "09:00",
                            "topic": "How I learned to code in 6 months",
                            "image": null
                        },
                        {
                            "time": "14:00",
                            "topic": "Common mistakes new freelancers make",
                            "image": null
                        },
                        {
                            "time": "19:00",
                            "topic": "Building a sustainable side hustle",
                            "image": "images/day2_evening.jpg"
                        }
                    ]
                }
            ]
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Sample config created: {self.config_file}")
    
    def get_today_threads(self) -> List[Dict]:
        """Get threads for today"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        for day in self.schedule:
            if day['date'] == today:
                return day['posts']
        return []
    
    def get_thread_by_time(self, target_time: str) -> Optional[Dict]:
        """Get thread for specific time slot"""
        threads = self.get_today_threads()
        
        for thread in threads:
            if thread['time'] == target_time:
                return thread
        return None
    
    def generate_and_post(self, thread_config: Dict) -> Dict:
        """Generate and post a thread"""
        topic = thread_config['topic']
        image = thread_config.get('image')
        
        print(f"\n{'='*70}")
        print(f"PROCESSING THREAD")
        print(f"{'='*70}")
        print(f"Topic: {topic}")
        print(f"Image: {image if image else 'None'}")
        print(f"{'='*70}")
        
        # Generate thread
        posts = self.generator.generate_thread(topic)
        
        if not posts:
            return {
                'status': 'failed',
                'reason': 'generation_failed',
                'topic': topic
            }
        
        # Check image exists
        if image and not os.path.exists(image):
            print(f"⚠️  Image not found, posting without image")
            image = None
        
        # Post to Bluesky
        result = self.publisher.post_thread(posts, image_path=image)
        
        if result:
            return {
                'status': 'success',
                'topic': topic,
                'posts': posts,
                'image': image,
                'uri': result[0]['uri'],
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'status': 'failed',
                'reason': 'posting_failed',
                'topic': topic
            }
    
    def run_time_slot(self, time_slot: str):
        """Run thread for specific time"""
        print(f"\n{'='*70}")
        print(f"BLUESKY AUTOMATION - {time_slot}")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*70}\n")
        
        thread = self.get_thread_by_time(time_slot)
        
        if not thread:
            print(f"⚠️  No thread scheduled for {time_slot}")
            return
        
        result = self.generate_and_post(thread)
        self._log_post(result)
        self._print_result(result)
    
    def run_all_today(self):
        """Run all threads for today"""
        threads = self.get_today_threads()
        
        if not threads:
            print(f"⚠️  No threads for today")
            return
        
        print(f"\n{'='*70}")
        print(f"RUNNING ALL TODAY'S THREADS")
        print(f"Total: {len(threads)}")
        print(f"{'='*70}\n")
        
        results = []
        for idx, thread in enumerate(threads, 1):
            print(f"\n[{idx}/{len(threads)}]")
            result = self.generate_and_post(thread)
            results.append(result)
            self._log_post(result)
            
            if idx < len(threads):
                print("\n⏳ Waiting 10 seconds...")
                time.sleep(10)
        
        self._print_summary(results)
    
    def _log_post(self, result: Dict):
        """Log posted thread"""
        log_file = 'bluesky_posts_log.json'
        logs = []
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        
        logs.append(result)
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    
    def _print_result(self, result: Dict):
        """Print single result"""
        print(f"\n{'='*70}")
        print(f"RESULT")
        print(f"{'='*70}")
        if result['status'] == 'success':
            print(f"✅ Thread posted!")
            print(f"   Topic: {result['topic']}")
            print(f"   Posts: {len(result['posts'])}")
        else:
            print(f"❌ Failed: {result.get('reason')}")
        print(f"{'='*70}\n")
    
    def _print_summary(self, results: List[Dict]):
        """Print summary"""
        success = sum(1 for r in results if r['status'] == 'success')
        
        print(f"\n{'='*70}")
        print(f"DAILY SUMMARY")
        print(f"{'='*70}")
        print(f"Total: {len(results)}")
        print(f"✅ Success: {success}")
        print(f"❌ Failed: {len(results) - success}")
        
        if success > 0:
            print(f"\nPosted threads:")
            for r in results:
                if r['status'] == 'success':
                    print(f"  • {r['topic']}")
        print(f"{'='*70}\n")
    
    def preview_schedule(self):
        """Preview schedule"""
        print(f"\n{'='*70}")
        print(f"BLUESKY SCHEDULE PREVIEW")
        print(f"{'='*70}\n")
        
        for day in self.schedule:
            print(f"Day {day['day']} ({day['date']}):")
            for post in day['posts']:
                print(f"  {post['time']}: {post['topic']}")
                if post.get('image'):
                    print(f"           Image: {post['image']}")
            print()
        print(f"{'='*70}\n")


if __name__ == '__main__':
    """
    Main entry point
    
    USAGE:
        python bluesky_automation.py 09:00     # Post 9am thread
        python bluesky_automation.py 14:00     # Post 2pm thread
        python bluesky_automation.py 19:00     # Post 7pm thread
        python bluesky_automation.py all       # Post all today
        python bluesky_automation.py preview   # Preview schedule
    """
    import sys
    
    try:
        automation = BlueskyAutomation()
        
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == 'all':
                automation.run_all_today()
            elif command == 'preview':
                automation.preview_schedule()
            elif ':' in command:  # Time format like 09:00
                automation.run_time_slot(command)
            else:
                print("Usage:")
                print("  python bluesky_automation.py 09:00")
                print("  python bluesky_automation.py 14:00")
                print("  python bluesky_automation.py 19:00")
                print("  python bluesky_automation.py all")
                print("  python bluesky_automation.py preview")
        else:
            automation.preview_schedule()
            
    except FileNotFoundError as e:
        print(f"\n{e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()