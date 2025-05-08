# Validador de Bucket S3

Este script Python utiliza o boto3 para gerenciar buckets S3 na AWS. Ele realiza as seguintes operações:

1. Cria um bucket chamado `mybucketvalidador` (se não existir)
2. Habilita o uso de ACL no bucket
3. Verifica se um e-mail possui conta AWS
4. Adiciona o e-mail à ACL do bucket se tiver conta AWS

## Pré-requisitos

- Python 3.6+
- Credenciais da AWS configuradas (via AWS CLI ou variáveis de ambiente)
- Permissões adequadas na conta AWS

## Instalação

1. Clone o repositório
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

## Uso

```bash
python s3_bucket_validator.py --email seu.email@exemplo.com
```

## Funcionalidades

- Verifica se o bucket `mybucketvalidador` existe
- Cria o bucket se não existir, habilitando ACL
- Verifica se o e-mail informado possui conta AWS
- Adiciona o e-mail à ACL do bucket se tiver conta AWS
- Fornece feedback claro sobre cada operação

## Permissões necessárias

O usuário AWS precisa ter as seguintes permissões:
- `s3:CreateBucket`
- `s3:PutBucketAcl`
- `s3:GetBucketAcl`
- `iam:GetAccountAuthorizationDetails`
- `iam:ListAccountAliases`
