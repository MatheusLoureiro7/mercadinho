"""
Cadastro — categoria, produto, fornecedor e usuário. Tarefa B1.

Tabelas (schema.sql): categoria, fornecedor, produto, usuario — nomes, colunas, tipos, padrões e
restrições exatamente como na Apostila IV, seção 6. Nada a mais.
Regras garantidas no banco: RN03 (ck_produto_rn03), RN14 (ck_usuario_papel).
"""

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models import Q


class Categoria(models.Model):
    """Agrupamento de produtos, no vocabulário da loja: "Secos e molhados", "Açougue", "Frios"."""

    nome = models.CharField(max_length=80, unique=True)
    perecivel_padrao = models.BooleanField(db_default=False)

    class Meta:
        db_table = "categoria"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Fornecedor(models.Model):
    nome = models.CharField(max_length=120)
    # Dias entre o pedido e a entrega: é o que faz o aviso de ruptura sair a tempo (RN08).
    prazo_entrega_dias = models.IntegerField()
    pedido_minimo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    contato = models.CharField(max_length=160, null=True, blank=True)  # noqa: DJ001 — nulo no schema.sql

    class Meta:
        db_table = "fornecedor"
        ordering = ["nome"]
        constraints = [
            models.CheckConstraint(condition=Q(prazo_entrega_dias__gte=0), name="ck_fornecedor_prazo"),
        ]

    def __str__(self):
        return self.nome


class Produto(models.Model):
    """
    ATENÇÃO: não existe coluna de saldo aqui. O saldo é derivado das movimentações (RN01).
    """

    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="produtos")
    fornecedor_padrao = models.ForeignKey(
        Fornecedor, on_delete=models.PROTECT, null=True, blank=True, related_name="produtos"
    )
    nome = models.CharField(max_length=160)
    unidade_medida = models.CharField(max_length=10)  # 'KG', 'UN', 'L', 'PCT'
    perecivel = models.BooleanField(db_default=False)
    durabilidade_dias = models.IntegerField(null=True, blank=True)  # obrigatório se perecível (RN03)
    preco_custo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    preco_venda = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estoque_minimo = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    # Itens que não podem faltar no fim de semana: carne, carvão, cerveja, linguiça, asinha (RN10).
    critico_fim_semana = models.BooleanField(db_default=False)

    class Meta:
        db_table = "produto"
        ordering = ["nome"]
        constraints = [
            # RN03: perecível só é salvo com durabilidade preenchida e maior que zero. A API valida
            # antes (tarefa B4, fluxograma 01); o banco é a última linha de defesa.
            models.CheckConstraint(
                condition=Q(perecivel=False) | Q(durabilidade_dias__isnull=False, durabilidade_dias__gt=0),
                name="ck_produto_rn03",
            ),
            # Fluxograma 01: "já existe produto com este nome na categoria?"
            models.UniqueConstraint(fields=["categoria", "nome"], name="uq_produto_nome_categoria"),
        ]

    def __str__(self):
        return self.nome


class GerenciadorDeUsuario(BaseUserManager):
    def create_user(self, login: str, senha: str, nome: str, papel: str, **extras):
        usuario = self.model(login=login, nome=nome, papel=papel, **extras)
        usuario.set_password(senha)  # grava só o hash, em senha_hash (RNF12)
        usuario.save(using=self._db)
        return usuario


class Usuario(AbstractBaseUser):
    """
    Usuário do sistema, sobre a tabela `usuario` exatamente como na Apostila IV (decisão da L09,
    docs/LACUNAS.md): o hash da senha fica em `senha_hash`, não existe `last_login`, e o controle
    de acesso é o `papel` (RN14) — não os grupos e permissões do Django.

    Só três pessoas têm usuário: o Sr. João (DONO), a esposa (GESTAO) e o sobrinho (OPERACAO).
    Os dois funcionários da loja não acessam o sistema.
    """

    class Papel(models.TextChoices):
        DONO = "DONO", "Dono"
        GESTAO = "GESTAO", "Gestão"
        OPERACAO = "OPERACAO", "Operação"

    nome = models.CharField(max_length=120)
    papel = models.CharField(max_length=10, choices=Papel.choices)
    login = models.CharField(max_length=60, unique=True)
    password = models.CharField("senha", max_length=255, db_column="senha_hash")
    telegram_chat_id = models.CharField(max_length=40, null=True, blank=True)  # noqa: DJ001 — só o DONO recebe aviso
    ativo = models.BooleanField(db_default=True)

    last_login = None  # não existe na Apostila IV (L09)

    objects = GerenciadorDeUsuario()

    USERNAME_FIELD = "login"
    REQUIRED_FIELDS = ["nome", "papel"]

    class Meta:
        db_table = "usuario"
        ordering = ["nome"]
        constraints = [
            # RN14: exatamente três perfis.
            models.CheckConstraint(
                condition=Q(papel__in=["DONO", "GESTAO", "OPERACAO"]), name="ck_usuario_papel"
            ),
        ]

    @property
    def is_active(self):
        # O Django recusa o login de quem não está ativo; aqui a coluna se chama `ativo`.
        return self.ativo

    def __str__(self):
        return self.nome
