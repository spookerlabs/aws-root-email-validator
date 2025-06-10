#!/usr/bin/env python3
import boto3
import sys
import argparse

# ANSI Colors
GREEN = '\033[92m'  # Green
RED = '\033[91m'    # Red
YELLOW = '\033[93m' # Yellow
RESET = '\033[0m'   # Reset

def check_aws_account(email):
    """Check if email has an AWS account"""
    try:
        sts = boto3.client('sts')
        sts.get_caller_identity()
        return True
    except Exception as e:
        print(f"Error checking AWS credentials: {str(e)}")
        return False

def create_bucket_if_not_exists(s3_client, bucket_name):
    """Create S3 bucket if it doesn't exist"""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return False
    except s3_client.exceptions.ClientError as e:
        error_code = e.response.get('Error', {}).get('Code')
        if error_code == '404':
            # Bucket doesn't exist, try to create it
            try:
                # Get current session region
                region = s3_client.meta.region_name
                
                # Configure bucket based on region
                if region == 'us-east-1':
                    s3_client.create_bucket(
                        Bucket=bucket_name,
                        ObjectOwnership='ObjectWriter',
                        ACL='private'
                    )
                else:
                    s3_client.create_bucket(
                        Bucket=bucket_name,
                        ObjectOwnership='ObjectWriter',
                        ACL='private',
                        CreateBucketConfiguration={
                            'LocationConstraint': region
                        }
                    )
                
                # Configure bucket ownership controls
                s3_client.put_public_access_block(
                    Bucket=bucket_name,
                    PublicAccessBlockConfiguration={
                        'BlockPublicAcls': False,
                        'IgnorePublicAcls': False,
                        'BlockPublicPolicy': True,
                        'RestrictPublicBuckets': True
                    }
                )
                return True
                
            except s3_client.exceptions.BucketAlreadyExists:
                print(f"{YELLOW}Warning: The bucket {bucket_name} already exists in another AWS account.{RESET}")
                return False
            except s3_client.exceptions.BucketAlreadyOwnedByYou:
                return False
            except Exception as e:
                print(f"{RED}Error creating bucket {bucket_name}: {str(e)}{RESET}")
                sys.exit(1)
        elif error_code == '403':
            print(f"{YELLOW}Warning: Access denied to bucket {bucket_name}. It might already exist in another account.{RESET}")
            return False
        else:
            print(f"{YELLOW}Warning: Error accessing bucket {bucket_name}: {str(e)}{RESET}")
            return False

def add_email_to_acl(s3_client, bucket_name, email):
    """Add email to bucket ACL"""
    try:
        grant = {
            'Grantee': {
                'Type': 'AmazonCustomerByEmail',
                'EmailAddress': email
            },
            'Permission': 'READ_ACP'  # Read ACL permission
        }
        
        acl = s3_client.get_bucket_acl(Bucket=bucket_name)
        acl['Grants'].append(grant)
        
        s3_client.put_bucket_acl(
            Bucket=bucket_name,
            AccessControlPolicy={
                'Owner': acl['Owner'],
                'Grants': acl['Grants']
            }
        )
        print(f"{GREEN}✓{RESET} {email} (AWS account found)")
    except s3_client.exceptions.ClientError as e:
        if 'UnresolvableGrantByEmailAddress' in str(e):
            print(f"{RED}✗{RESET} {email} (No AWS account)")
        else:
            print(f"{RED}Error adding permission for {email}: {str(e)}{RESET}")
    except Exception as e:
        print(f"{RED}Unexpected error processing {email}: {str(e)}{RESET}")

def process_emails(s3, bucket_name, emails):
    """Process a list of email addresses"""
    print("\nChecking emails...\n")
    for email in emails:
        email = email.strip()
        if not email:
            continue
            
        try:
            if check_aws_account(email):
                add_email_to_acl(s3, bucket_name, email)
        except Exception as e:
            print(f"{RED}Error processing email {email}: {str(e)}{RESET}")
    print()  # Add an empty line at the end

def main():
    parser = argparse.ArgumentParser(description='AWS Account Email Validator')
    parser.add_argument('--bucket', required=True, help='S3 bucket name')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--email', help='Email to verify and grant permission')
    group.add_argument('--file', help='File containing list of emails (one per line)')
    
    args = parser.parse_args()
    
    try:
        s3 = boto3.client('s3')
        
        # Create bucket if it doesn't exist
        create_bucket_if_not_exists(s3, args.bucket)
        
        # Process single email or file
        if args.email:
            process_emails(s3, args.bucket, [args.email])
        elif args.file:
            try:
                with open(args.file, 'r') as f:
                    emails = f.readlines()
                    process_emails(s3, args.bucket, emails)
            except FileNotFoundError:
                print(f"{RED}File not found: {args.file}{RESET}")
                sys.exit(1)
        
    except Exception as e:
        print(f"{RED}Unexpected error: {str(e)}{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
