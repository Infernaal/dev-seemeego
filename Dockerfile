FROM python:3.10-slim

# ���������� pip � ��������� ������������
RUN pip install --upgrade pip

WORKDIR /seemeego-ai

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# �������� �� ����������
COPY . .

# �������, ��� ����� temp-seemeego ����������
RUN mkdir -p /seemeego-ai/temp-seemeego

# ������ �������� �������
CMD ["python", "seemeego_main.py"]