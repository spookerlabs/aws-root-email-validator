# Validador se um e-mail possui conta na AWS

Este script Python utiliza o boto3 para descobrir se um e-mail tem contas na AWS. Ele realiza as seguintes operações:

1. Cria um bucket chamado `<name que escolher --bucket>` 
2. Habilita o uso de ACL no bucket
3. Verifica se um e-mail possui conta AWS

## Pré-requisitos

- Python 3.6+
- Credenciais da AWS configuradas (via AWS CLI ou variáveis de ambiente)
- Permissões adequadas na conta AWS
- Boto3

## Uso

```
python3 -mvenv virtual
source virtual/bin/activate
pip3 install boto3
```
```bash
python aws-email-root-validator.py --email seu.email@exemplo.com

python aws-email-root-validator.py --file email-list.txt
```

# Exemplos

![image](https://github.com/user-attachments/assets/a0153226-d8ce-4cb2-99f3-9a00fe3bd185)

![image](https://github.com/user-attachments/assets/e955d151-f3bb-4034-afc5-690ea5c5cd4b)

