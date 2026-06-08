from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    PERFIL_ADMIN = 'admin'
    PERFIL_USER = 'user'
    PERFIL_CHOICES = [
        (PERFIL_ADMIN, 'Administrador'),
        (PERFIL_USER, 'Usuário'),
    ]
    perfil = models.CharField(max_length=10, choices=PERFIL_CHOICES, default=PERFIL_USER)

    def is_admin_inventario(self):
        return self.perfil == self.PERFIL_ADMIN or self.is_superuser

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'


class DataCenter(models.Model):
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
    cidade = models.CharField(max_length=100)
    observacoes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.nome} ({self.codigo})'

    class Meta:
        verbose_name = 'Data Center'
        verbose_name_plural = 'Data Centers'
        ordering = ['nome']


class TipoComponente(models.Model):
    DISCO = 'disco'
    RAM = 'ram'
    CPU = 'cpu'
    PSU = 'psu'
    CUSTOM = 'custom'

    CATEGORIA_CHOICES = [
        (DISCO, 'Disco'),
        (RAM, 'Memória RAM'),
        (CPU, 'CPU (Processador)'),
        (PSU, 'Fonte de Alimentação (PSU)'),
        (CUSTOM, 'Personalizado'),
    ]

    nome = models.CharField(max_length=100, unique=True)
    categoria = models.CharField(max_length=10, choices=CATEGORIA_CHOICES, default=DISCO)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    def pode_remover(self):
        return not self.componente_set.exists()

    class Meta:
        verbose_name = 'Tipo de Componente'
        verbose_name_plural = 'Tipos de Componentes'
        ordering = ['nome']


class Fabricante(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    tipos = models.ManyToManyField(TipoComponente, blank=True, related_name='fabricantes')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Fabricante'
        verbose_name_plural = 'Fabricantes'
        ordering = ['nome']


class LimiteEstoque(models.Model):
    tipo = models.ForeignKey(TipoComponente, on_delete=models.CASCADE)
    data_center = models.ForeignKey(DataCenter, on_delete=models.CASCADE)
    minimo = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('tipo', 'data_center')
        verbose_name = 'Limite de Estoque'
        verbose_name_plural = 'Limites de Estoque'

    def __str__(self):
        return f'{self.tipo} @ {self.data_center}: mín {self.minimo}'


class Componente(models.Model):
    EM_ESTOQUE = 'em_estoque'
    REMOVIDO = 'removido'

    STATUS_CHOICES = [
        (EM_ESTOQUE, 'Em estoque'),
        (REMOVIDO, 'Removido'),
    ]

    # Campos comuns
    tipo = models.ForeignKey(TipoComponente, on_delete=models.PROTECT)
    fabricante = models.ForeignKey(Fabricante, on_delete=models.PROTECT)
    modelo = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=EM_ESTOQUE)
    data_center = models.ForeignKey(DataCenter, on_delete=models.PROTECT)
    data_entrada = models.DateField(auto_now_add=True)
    observacoes = models.TextField(blank=True)

    # Campos específicos — Disco
    DISCO_HDD = 'HDD'
    DISCO_SSD = 'SSD'
    DISCO_NVME = 'NVMe'
    DISCO_TIPO_CHOICES = [(x, x) for x in [DISCO_HDD, DISCO_SSD, DISCO_NVME]]

    INTERFACE_SATA = 'SATA'
    INTERFACE_SAS = 'SAS'
    INTERFACE_NVME = 'NVMe'
    INTERFACE_CHOICES = [(x, x) for x in [INTERFACE_SATA, INTERFACE_SAS, INTERFACE_NVME]]

    CAPACIDADE_DISCO_CHOICES = [(x, x) for x in [
        '500GB', '1TB', '2TB', '4TB', '8TB', '12TB', '16TB', '18TB'
    ]]

    disco_capacidade = models.CharField(max_length=10, blank=True, choices=CAPACIDADE_DISCO_CHOICES)
    disco_tipo = models.CharField(max_length=5, blank=True, choices=DISCO_TIPO_CHOICES)
    disco_interface = models.CharField(max_length=5, blank=True, choices=INTERFACE_CHOICES)

    def __str__(self):
        return f'{self.fabricante} {self.modelo} [{self.get_status_display()}]'

    class Meta:
        verbose_name = 'Componente'
        verbose_name_plural = 'Componentes'
        ordering = ['-data_entrada']


class Movimentacao(models.Model):
    ENTRADA = 'entrada'
    SAIDA = 'saida'

    TIPO_CHOICES = [
        (ENTRADA, 'Entrada'),
        (SAIDA, 'Saída'),
    ]

    componente = models.ForeignKey(Componente, on_delete=models.CASCADE, related_name='movimentacoes')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    data = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    observacoes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.componente} em {self.data:%d/%m/%Y}'

    class Meta:
        verbose_name = 'Movimentação'
        verbose_name_plural = 'Movimentações'
        ordering = ['-data']
