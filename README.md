# Validador de cont

Este script Python utiliza o boto3 para descobrir se um e-mail tem contas na AWS. Ele realiza as seguintes operações:

1. Cria um bucket chamado `<name que escolher cli>` (se não existir)
2. Habilita o uso de ACL no bucket
3. Verifica se um e-mail possui conta AWS
4. 
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
python aws-email-root-validator.py --email seu.email@exemplo.com

python aws-email-root-validator.py --file email-list.txt
```

# Exemplos

aws-email-root-validator % python3 aws-email-root-validator.py --bucket awsemailvalidator --email spooker@gmail.com

Verificando e-mails...

✓ spooker@gmail.com (Conta AWS encontrada)


aws-email-root-validator % python3 aws-email-root-validator.py --bucket awsemailvalidator --file emails.txt

Verificando e-mails...

✗ spooker+cloudgoat@gmail.com (Sem conta AWS)
✓ aws@amazonaws.com (Conta AWS encontrada)
✓ spooker@gmail.com (Conta AWS encontrada)
✗ spooker+alias123@gmail.com (Sem conta AWS)
✗ rodrigo.montoro@clavis.com.br (Sem conta AWS)
✓ spooker+dataperimeterorganizations@gmail.com (Conta AWS encontrada)
✗ spooker+dataperimeterlabs@gmail.com (Sem conta AWS)
