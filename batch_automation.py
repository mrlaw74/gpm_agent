"""
Batch Automation Example for GPM-Login Python Agent

This script demonstrates how to run automation tasks across multiple profiles
in batch mode with proper error handling and reporting.
"""

import sys
import os
import time
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gpm_client import GPMClient, GPMClientError


def simulate_web_task(profile_info, task_config):
    """
    Simulate a web automation task
    
    Args:
        profile_info: Profile information from GPM
        task_config: Task configuration
        
    Returns:
        dict: Task result
    """
    profile_id = profile_info.get('id')
    profile_name = profile_info.get('name')
    
    print(f"    Running task on profile: {profile_name}")
    
    # Simulate task execution time
    execution_time = task_config.get('execution_time', 2)
    time.sleep(execution_time)
    
    # Simulate some results
    result = {
        'profile_id': profile_id,
        'profile_name': profile_name,
        'task_type': task_config.get('type', 'unknown'),
        'execution_time': execution_time,
        'timestamp': datetime.now().isoformat(),
        'status': 'completed',
        'data': {
            'pages_visited': task_config.get('pages', 1),
            'actions_performed': task_config.get('actions', 3),
            'success_rate': 0.95
        }
    }
    
    return result


def create_test_profiles(client, count=3):
    """Create test profiles for batch automation"""
    print(f"Creating {count} test profiles...")
    
    created_profiles = []
    
    for i in range(count):
        try:
            profile_name = f"Batch Test Profile {i+1} - {int(time.time())}"
            
            profile = client.create_default_profile(
                name=profile_name,
                group_name="Batch Test",
                os="Windows 11"
            )
            
            created_profiles.append(profile['data'])
            print(f"  ✓ Created: {profile_name}")
            
        except Exception as e:
            print(f"  ✗ Failed to create profile {i+1}: {e}")
    
    return created_profiles


def batch_automation_simple(client, profiles, task_configs):
    """
    Simple batch automation without Selenium
    
    Args:
        client: GPM client instance
        profiles: List of profile data
        task_configs: List of task configurations
        
    Returns:
        list: Results from all tasks
    """
    print(f"\nRunning batch automation on {len(profiles)} profiles...")
    
    results = []
    
    for i, profile in enumerate(profiles):
        profile_id = profile['id']
        profile_name = profile['name']
        
        print(f"\n[{i+1}/{len(profiles)}] Processing profile: {profile_name}")
        
        try:
            # Start the profile
            print(f"  Starting profile...")
            browser_info = client.start_profile(profile_id, win_scale=0.6)
            debug_address = browser_info['data']['remote_debugging_address']
            print(f"  ✓ Profile started: {debug_address}")
            
            # Execute tasks for this profile
            profile_results = []
            
            for task_config in task_configs:
                print(f"  Executing task: {task_config['type']}")
                task_result = simulate_web_task(profile, task_config)
                profile_results.append(task_result)
            
            # Stop the profile
            print(f"  Stopping profile...")
            client.stop_profile(profile_id)
            print(f"  ✓ Profile stopped")
            
            results.append({
                'profile_id': profile_id,
                'profile_name': profile_name,
                'success': True,
                'tasks': profile_results,
                'error': None
            })
            
            # Small delay between profiles
            time.sleep(1)
            
        except Exception as e:
            print(f"  ✗ Error processing profile {profile_name}: {e}")
            
            # Try to stop profile in case of error
            try:
                client.stop_profile(profile_id)
            except:
                pass
            
            results.append({
                'profile_id': profile_id,
                'profile_name': profile_name,
                'success': False,
                'tasks': [],
                'error': str(e)
            })
    
    return results


def parallel_batch_automation(client, profiles, task_configs, max_concurrent=2):
    """
    Parallel batch automation with concurrency control
    
    Args:
        client: GPM client instance
        profiles: List of profile data
        task_configs: List of task configurations
        max_concurrent: Maximum concurrent profiles to run
        
    Returns:
        list: Results from all tasks
    """
    print(f"\nRunning parallel batch automation (max {max_concurrent} concurrent)...")
    
    import threading
    import queue
    
    results = []
    results_lock = threading.Lock()
    
    def worker(profile_queue, results_list):
        """Worker thread for processing profiles"""
        while True:
            try:
                profile = profile_queue.get_nowait()
            except queue.Empty:
                break
            
            profile_id = profile['id']
            profile_name = profile['name']
            thread_name = threading.current_thread().name
            
            print(f"[{thread_name}] Processing profile: {profile_name}")
            
            try:
                # Start the profile
                browser_info = client.start_profile(profile_id, win_scale=0.5)
                debug_address = browser_info['data']['remote_debugging_address']
                print(f"[{thread_name}] Profile started: {debug_address}")
                
                # Execute tasks
                profile_results = []
                for task_config in task_configs:
                    task_result = simulate_web_task(profile, task_config)
                    profile_results.append(task_result)
                
                # Stop the profile
                client.stop_profile(profile_id)
                print(f"[{thread_name}] Profile stopped: {profile_name}")
                
                with results_lock:
                    results_list.append({
                        'profile_id': profile_id,
                        'profile_name': profile_name,
                        'success': True,
                        'tasks': profile_results,
                        'error': None
                    })
                
            except Exception as e:
                print(f"[{thread_name}] Error processing {profile_name}: {e}")
                
                try:
                    client.stop_profile(profile_id)
                except:
                    pass
                
                with results_lock:
                    results_list.append({
                        'profile_id': profile_id,
                        'profile_name': profile_name,
                        'success': False,
                        'tasks': [],
                        'error': str(e)
                    })
            
            finally:
                profile_queue.task_done()
    
    # Create queue and add profiles
    profile_queue = queue.Queue()
    for profile in profiles:
        profile_queue.put(profile)
    
    # Create and start worker threads
    threads = []
    for i in range(min(max_concurrent, len(profiles))):
        thread = threading.Thread(target=worker, args=(profile_queue, results))
        thread.name = f"Worker-{i+1}"
        thread.start()
        threads.append(thread)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    return results


def generate_report(results, output_file="batch_report.json"):
    """Generate detailed report from batch automation results"""
    
    print(f"\nGenerating batch automation report...")
    
    # Calculate statistics
    total_profiles = len(results)
    successful_profiles = sum(1 for r in results if r['success'])
    failed_profiles = total_profiles - successful_profiles
    
    total_tasks = sum(len(r['tasks']) for r in results)
    
    # Create report
    report = {
        'summary': {
            'timestamp': datetime.now().isoformat(),
            'total_profiles': total_profiles,
            'successful_profiles': successful_profiles,
            'failed_profiles': failed_profiles,
            'success_rate': successful_profiles / total_profiles if total_profiles > 0 else 0,
            'total_tasks': total_tasks
        },
        'results': results
    }
    
    # Save to file
    try:
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"✓ Report saved to: {output_file}")
    except Exception as e:
        print(f"✗ Failed to save report: {e}")
    
    # Print summary
    print(f"\n--- Batch Automation Summary ---")
    print(f"Total Profiles: {total_profiles}")
    print(f"Successful: {successful_profiles}")
    print(f"Failed: {failed_profiles}")
    print(f"Success Rate: {report['summary']['success_rate']:.1%}")
    print(f"Total Tasks: {total_tasks}")
    
    if failed_profiles > 0:
        print(f"\nFailed Profiles:")
        for result in results:
            if not result['success']:
                print(f"  - {result['profile_name']}: {result['error']}")
    
    return report


def cleanup_test_profiles(client, profiles):
    """Clean up test profiles"""
    print(f"\nCleaning up {len(profiles)} test profiles...")
    
    for profile in profiles:
        try:
            profile_id = profile['id']
            profile_name = profile['name']
            
            # Try to stop first (in case still running)
            try:
                client.stop_profile(profile_id)
            except:
                pass
            
            # Delete profile
            # Uncomment the line below to actually delete profiles
            # client.delete_profile(profile_id)
            print(f"  ✓ Cleaned up: {profile_name}")
            
        except Exception as e:
            print(f"  ✗ Failed to cleanup {profile['name']}: {e}")


def main():
    """Main batch automation demonstration"""
    print("GPM-Login Batch Automation Example")
    print("=" * 50)
    
    # Initialize client
    try:
        client = GPMClient()
        
        # Test connection
        profiles_response = client.list_profiles(per_page=1)
        print(f"✓ Connected to GPM-Login API")
        print(f"  Total profiles available: {profiles_response['pagination']['total']}")
        
    except Exception as e:
        print(f"✗ Failed to connect to GPM-Login: {e}")
        return False
    
    # Task configurations
    task_configs = [
        {
            'type': 'navigation_test',
            'pages': 2,
            'actions': 5,
            'execution_time': 1
        },
        {
            'type': 'form_interaction',
            'pages': 1,
            'actions': 3,
            'execution_time': 1.5
        }
    ]
    
    # Option 1: Use existing profiles
    existing_profiles = client.list_profiles(per_page=3)['data']
    
    if existing_profiles:
        print(f"\nOption 1: Using existing profiles ({len(existing_profiles)} available)")
        
        # Run simple batch automation
        results1 = batch_automation_simple(client, existing_profiles[:2], task_configs)
        
        # Generate report
        report1 = generate_report(results1, "existing_profiles_report.json")
    
    # Option 2: Create test profiles for demonstration
    print(f"\nOption 2: Creating test profiles for demonstration")
    
    test_profiles = create_test_profiles(client, count=3)
    
    if test_profiles:
        # Run parallel batch automation
        results2 = parallel_batch_automation(client, test_profiles, task_configs, max_concurrent=2)
        
        # Generate report
        report2 = generate_report(results2, "test_profiles_report.json")
        
        # Cleanup
        cleanup_test_profiles(client, test_profiles)
    
    print(f"\n🎉 Batch automation demonstration completed!")
    print(f"Check the generated JSON reports for detailed results.")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nBatch automation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
