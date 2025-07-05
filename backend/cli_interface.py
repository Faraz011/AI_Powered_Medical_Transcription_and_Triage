import re
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import argparse
import sys
from pathlib import Path
from mainPipeline import MedicalPipelineIntegrator

def create_parser():
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="AI-Powered Medical Transcription and Triage Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli_interface.py single audio.wav --patient-id "P001"
  python cli_interface.py batch ./audio_folder/
  python cli_interface.py batch ./audio_folder/ --mapping patients.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Single file processing
    single_parser = subparsers.add_parser('single', help='Process single audio file')
    single_parser.add_argument('audio_file', help='Path to audio file')
    single_parser.add_argument('--patient-id', help='Patient identifier')
    single_parser.add_argument('--config', help='Configuration file path')
    
    # Batch processing
    batch_parser = subparsers.add_parser('batch', help='Process multiple audio files')
    batch_parser.add_argument('audio_directory', help='Directory containing audio files')
    batch_parser.add_argument('--mapping', help='JSON file mapping filenames to patient IDs')
    batch_parser.add_argument('--config', help='Configuration file path')
    
    return parser

def main():
    """Main CLI function"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # Initialize pipeline
        pipeline = MedicalPipelineIntegrator(config_path=args.config)
        
        if args.command == 'single':
            # Process single file
            result = pipeline.process_single_audio(
                args.audio_file, 
                patient_id=getattr(args, 'patient_id', None)
            )
            
            if result.get('status') == 'completed':
                print(f" Successfully processed: {args.audio_file}")
                print(f" Session ID: {result['session_info']['session_id']}")
                print(f" Triage Level: {result['triage']['triage_level']}")
                print(f"  Priority: {result['triage'].get('priority', 'Unknown')}")
            else:
                print(f"Processing failed: {result.get('error', 'Unknown error')}")
                
        elif args.command == 'batch':
            # Load patient mapping if provided
            patient_mapping = None
            if hasattr(args, 'mapping') and args.mapping:
                import json
                with open(args.mapping, 'r') as f:
                    patient_mapping = json.load(f)
            
            # Process batch
            results = pipeline.process_batch_audio(
                args.audio_directory,
                patient_mapping=patient_mapping
            )
            
            successful = sum(1 for r in results if r.get('status') == 'completed')
            print(f"✅ Batch processing completed: {successful}/{len(results)} successful")
            
    except Exception as e:
        print(f"Pipeline error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
