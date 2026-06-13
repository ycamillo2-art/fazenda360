from django.db import models

class Propriedade(models.Model):
    nome = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Propriedades"

class Categoria(models.Model):
    nome = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nome

class Subcategoria(models.Model):
    nome = models.CharField(max_length=255)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='subcategorias')

    def __str__(self):
        return f"{self.categoria.nome} - {self.nome}"

    class Meta:
        unique_together = ('nome', 'categoria')

class Tipo(models.Model):
    nome = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nome

class Lancamento(models.Model):
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE)
    data = models.DateField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.CASCADE)
    tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.data} - {self.propriedade} - {self.valor}"

    class Meta:
        ordering = ['-data']

class Cotacao(models.Model):
    tipo = models.CharField(max_length=50) # Conilon 7, 7/8, 8
    preco = models.CharField(max_length=50)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tipo}: {self.preco}"

    class Meta:
        verbose_name_plural = "Cotações"
