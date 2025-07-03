#!/usr/bin/env python3
"""
Cleanup service for removing files older than 24 hours
"""

import os
import time
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
CLEANUP_INTERVAL = int(os.environ.get('CLEANUP_INTERVAL', 3600))  # 1 hour
TTL_HOURS = int(os.environ.get('TTL_HOURS', 24))  # 24 hours
DIRECTORIES = ['/uploads', '/temp', '/audio']

def cleanup_old_files(directory, ttl_hours):
    """Remove files older than ttl_hours from directory"""
    if not os.path.exists(directory):
        logger.warning(f"Directory {directory} does not exist")
        return
    
    cutoff_time = datetime.now() - timedelta(hours=ttl_hours)
    removed_count = 0
    total_size = 0
    
    try:
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            
            if os.path.isfile(filepath):
                file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_mtime < cutoff_time:
                    try:
                        file_size = os.path.getsize(filepath)
                        os.remove(filepath)
                        removed_count += 1
                        total_size += file_size
                        logger.info(f"Removed {filepath} (age: {datetime.now() - file_mtime})")
                    except Exception as e:
                        logger.error(f"Failed to remove {filepath}: {e}")
        
        if removed_count > 0:
            logger.info(f"Cleanup complete for {directory}: {removed_count} files removed, {total_size / 1024 / 1024:.2f} MB freed")
        else:
            logger.debug(f"No old files found in {directory}")
            
    except Exception as e:
        logger.error(f"Error cleaning up {directory}: {e}")

def main():
    """Main cleanup loop"""
    logger.info(f"Starting cleanup service (TTL: {TTL_HOURS}h, Interval: {CLEANUP_INTERVAL}s)")
    
    while True:
        try:
            logger.info("Starting cleanup cycle...")
            
            for directory in DIRECTORIES:
                cleanup_old_files(directory, TTL_HOURS)
            
            logger.info(f"Cleanup cycle complete. Sleeping for {CLEANUP_INTERVAL} seconds...")
            time.sleep(CLEANUP_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("Cleanup service stopped")
            break
        except Exception as e:
            logger.error(f"Unexpected error in cleanup cycle: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

if __name__ == '__main__':
    main()