#!/usr/bin/env python3
import boto3
import sys
import argparse

# Cores ANSI
GREEN = '\033[92m'  # Verde
RED = '\033[91m'    # Vermelho
YELLOW = '\033[93m' # Amarelo
RESET = '\033[0m'   # Reset

def check_aws_account(email):
    """Check if email has an AWS account"""
    try:
        sts = boto3.client('sts')
        sts.get_caller_identity()
        return True
    except Exception as e:
        print(f"Erro ao verificar credenciais AWS: {str(e)}")
        return False

def create_bucket_if_not_exists(s3_client, bucket_name):
    """Create S3 bucket if it doesn't exist"""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return False
    except s3_client.exceptions.ClientError as e:
        error_code = e.response.get('Error', {}).get('Code')
        if error_code == '404':
            # Bucket não existe, vamos tentar criar
            try:
                # Obtém a região atual da sessão
                region = s3_client.meta.region_name
                
                # Configuração do bucket baseada na região
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
                
                # Configura a política de propriedade do bucket
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
                print(f"{YELLOW}Aviso: O bucket {bucket_name} já existe em outra conta AWS.{RESET}")
                return False
            except s3_client.exceptions.BucketAlreadyOwnedByYou:
                return False
            except Exception as e:
                print(f"{RED}Erro ao criar o bucket {bucket_name}: {str(e)}{RESET}")
                sys.exit(1)
        elif error_code == '403':
            print(f"{YELLOW}Aviso: Acesso negado ao bucket {bucket_name}. Pode já existir em outra conta.{RESET}")
            return False
        else:
            print(f"{YELLOW}Aviso: Erro ao acessar o bucket {bucket_name}: {str(e)}{RESET}")
            return False

def add_email_to_acl(s3_client, bucket_name, email):
    """Add email to bucket ACL"""
    try:
        grant = {
            'Grantee': {
                'Type': 'AmazonCustomerByEmail',
                'EmailAddress': email
            },
            'Permission': 'READ_ACP'  # Permissão de leitura da ACL
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
        print(f"{GREEN}✓{RESET} {email} (Conta AWS encontrada)")
    except s3_client.exceptions.ClientError as e:
        if 'UnresolvableGrantByEmailAddress' in str(e):
            print(f"{RED}✗{RESET} {email} (Sem conta AWS)")
        else:
            print(f"{RED}Erro ao adicionar permissão para {email}: {str(e)}{RESET}")
    except Exception as e:
        print(f"{RED}Erro inesperado ao processar {email}: {str(e)}{RESET}")

def process_emails(s3, bucket_name, emails):
    """Process a list of email addresses"""
    print("\nVerificando e-mails...\n")
    for email in emails:
        email = email.strip()
        if not email:
            continue
            
        try:
            if check_aws_account(email):
                add_email_to_acl(s3, bucket_name, email)
        except Exception as e:
            print(f"{RED}Erro ao processar e-mail {email}: {str(e)}{RESET}")
    print()  # Adiciona uma linha em branco no final

def main():
    parser = argparse.ArgumentParser(description='Validador de existencia conta em um e-mail')
    parser.add_argument('--bucket', required=True, help='Nome do bucket S3')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--email', help='E-mail para verificação e permissão')
    group.add_argument('--file', help='Arquivo com lista de e-mails (um por linha)')
    
    args = parser.parse_args()
    
    try:
        s3 = boto3.client('s3')
        
        # Criar bucket se não existir
        create_bucket_if_not_exists(s3, args.bucket)
        
        # Processar e-mail único ou arquivo
        if args.email:
            process_emails(s3, args.bucket, [args.email])
        elif args.file:
            try:
                with open(args.file, 'r') as f:
                    emails = f.readlines()
                    process_emails(s3, args.bucket, emails)
            except FileNotFoundError:
                print(f"{RED}Arquivo não encontrado: {args.file}{RESET}")
                sys.exit(1)
        
    except Exception as e:
        print(f"{RED}Erro inesperado: {str(e)}{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
