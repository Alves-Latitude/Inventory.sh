from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    PERFIL_ADMIN = 'admin'
    PERFIL_USER = 'user'
    PERFIL_LEITURA = 'leitura'
    PERFIL_CHOICES = [
        (PERFIL_ADMIN, 'Administrador'),
        (PERFIL_USER, 'Usuário'),
        (PERFIL_LEITURA, 'Viewer'),
    ]
    perfil = models.CharField(max_length=10, choices=PERFIL_CHOICES, default=PERFIL_USER)

    def is_admin_inventario(self):
        return self.perfil == self.PERFIL_ADMIN or self.is_superuser

    def is_somente_leitura(self):
        return self.perfil == self.PERFIL_LEITURA and not self.is_superuser

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


class Servidor(models.Model):
    """Cadastro leve de servidor — substitui o antigo campo de texto livre."""
    hostname = models.CharField(max_length=150)
    data_center = models.ForeignKey(DataCenter, on_delete=models.PROTECT, related_name='servidores')
    observacoes = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.hostname} ({self.data_center.codigo})'

    class Meta:
        verbose_name = 'Servidor'
        verbose_name_plural = 'Servidores'
        unique_together = ('hostname', 'data_center')
        ordering = ['hostname']


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


class PecaPadrao(models.Model):
    """Catálogo de peças padrão de troca/compra do datacenter — acelera o cadastro."""
    tipo = models.ForeignKey(TipoComponente, on_delete=models.CASCADE, related_name='pecas_padrao')
    fabricante = models.ForeignKey(Fabricante, on_delete=models.CASCADE, related_name='pecas_padrao')
    modelo = models.CharField(max_length=200)

    disco_capacidade = models.CharField(max_length=10, blank=True)
    disco_tipo = models.CharField(max_length=5, blank=True)
    disco_interface = models.CharField(max_length=5, blank=True)

    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.fabricante} {self.modelo}'

    class Meta:
        verbose_name = 'Peça Padrão'
        verbose_name_plural = 'Peças Padrão'
        ordering = ['tipo', 'fabricante', 'modelo']


class Componente(models.Model):
    EM_ESTOQUE = 'em_estoque'
    INSTALADO = 'instalado'
    REMOVIDO = 'removido'

    STATUS_CHOICES = [
        (EM_ESTOQUE, 'Em estoque'),
        (INSTALADO, 'Instalado'),
        (REMOVIDO, 'Removido'),
    ]

    tipo = models.ForeignKey(TipoComponente, on_delete=models.PROTECT)
    fabricante = models.ForeignKey(Fabricante, on_delete=models.PROTECT)
    modelo = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=EM_ESTOQUE)
    data_center = models.ForeignKey(DataCenter, on_delete=models.PROTECT)
    data_entrada = models.DateField(auto_now_add=True)
    observacoes = models.TextField(blank=True)

    numero_serie = models.CharField(
        'Número de série', max_length=100, blank=True, null=True, unique=True,
    )
    codigo_patrimonio = models.CharField(
        'Código patrimonial', max_length=100, blank=True, null=True, unique=True,
    )
    servidor = models.ForeignKey(
        Servidor, on_delete=models.SET_NULL, null=True, blank=True, related_name='componentes',
    )

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
    INSTALACAO = 'instalacao'
    SAIDA = 'saida'

    TIPO_CHOICES = [
        (ENTRADA, 'Entrada'),
        (INSTALACAO, 'Instalação'),
        (SAIDA, 'Saída'),
    ]

    componente = models.ForeignKey(Componente, on_delete=models.CASCADE, related_name='movimentacoes')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    servidor = models.ForeignKey(Servidor, on_delete=models.SET_NULL, null=True, blank=True)
    data = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    observacoes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.componente} em {self.data:%d/%m/%Y}'

    class Meta:
        verbose_name = 'Movimentação'
        verbose_name_plural = 'Movimentações'
        ordering = ['-data']


class HistoricoAlteracao(models.Model):
    """Log de auditoria: quem alterou o quê e quando, em cada componente."""
    componente = models.ForeignKey(Componente, on_delete=models.CASCADE, related_name='historico')
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    data = models.DateTimeField(auto_now_add=True)
    campo = models.CharField(max_length=50)
    valor_anterior = models.CharField(max_length=255, blank=True)
    valor_novo = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.componente} — {self.campo}: {self.valor_anterior} → {self.valor_novo}'

    class Meta:
        verbose_name = 'Histórico de Alteração'
        verbose_name_plural = 'Histórico de Alterações'
        ordering = ['-data']