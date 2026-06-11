from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse
from .models import Propriedade, Categoria, Subcategoria, Tipo, Lancamento
from datetime import datetime
import io
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend

@login_required
def exportar_excel(request):
    lancamentos = Lancamento.objects.all().order_by('-data')
    prop_id = request.GET.get('propriedade')
    mes = request.GET.get('month')
    cat_id = request.GET.get('categoria')

    if prop_id:
        lancamentos = lancamentos.filter(propriedade_id=prop_id)
    if mes:
        try:
            ano, mes_num = mes.split('-')
            lancamentos = lancamentos.filter(data__year=ano, data__month=mes_num)
        except:
            pass
    if cat_id:
        lancamentos = lancamentos.filter(categoria_id=cat_id)

    data = []
    for l in lancamentos:
        data.append({
            'Data': l.data.strftime('%d/%m/%Y'),
            'Propriedade': l.propriedade.nome,
            'Categoria': l.categoria.nome,
            'Subcategoria': l.subcategoria.nome,
            'Tipo': l.tipo.nome,
            'Valor': float(l.valor),
            'Descrição': l.descricao or "-"
        })

    df = pd.DataFrame(data)
    
    # Criar buffer em memória
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Lançamentos')
        
        # Ajustar largura das colunas automaticamente
        worksheet = writer.sheets['Lançamentos']
        for idx, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.column_dimensions[chr(65 + idx)].width = max_len
    
    buffer.seek(0)
    
    response = HttpResponse(
        buffer.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    response['Content-Disposition'] = f'attachment; filename="Backup_Fazenda360_{timestamp}.xlsx"'
    
    return response

def index(request):
    return render(request, 'financeiro/portal.html')

@login_required
def cadastro(request):
    if request.method == 'POST':
        prop_id = request.POST.get('propriedade')
        cat_id = request.POST.get('categoria')
        subcat_id = request.POST.get('subcategoria')
        tipo_id = request.POST.get('tipo')
        valor_str = request.POST.get('valor', '0').replace('.', '').replace(',', '.')
        data_str = request.POST.get('data')
        descricao = request.POST.get('descricao')

        try:
            if prop_id == 'new':
                prop, _ = Propriedade.objects.get_or_create(nome=request.POST.get('nova_propriedade'))
                prop_id = prop.id
            if cat_id == 'new':
                cat, _ = Categoria.objects.get_or_create(nome=request.POST.get('nova_categoria'))
                cat_id = cat.id
            if subcat_id == 'new':
                subcat, _ = Subcategoria.objects.get_or_create(
                    nome=request.POST.get('nova_subcategoria'),
                    categoria_id=cat_id
                )
                subcat_id = subcat.id
            if tipo_id == 'new':
                tipo, _ = Tipo.objects.get_or_create(nome=request.POST.get('novo_tipo'))
                tipo_id = tipo.id

            Lancamento.objects.create(
                propriedade_id=prop_id,
                categoria_id=cat_id,
                subcategoria_id=subcat_id,
                tipo_id=tipo_id,
                valor=valor_str,
                data=data_str,
                descricao=descricao
            )
            messages.success(request, 'Lançamento realizado com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao salvar: {str(e)}')
            
        return redirect('cadastro')

    propriedades = Propriedade.objects.all()
    categorias = Categoria.objects.all()
    subcategorias = Subcategoria.objects.all()
    tipos = Tipo.objects.all()
    
    context = {
        'propriedades': propriedades,
        'categorias': categorias,
        'subcategorias': subcategorias,
        'tipos': tipos,
        'hoje': datetime.now().strftime('%Y-%m-%d')
    }
    return render(request, 'financeiro/cadastro.html', context)

@login_required
def relatorios(request):
    lancamentos = Lancamento.objects.all().order_by('-data')
    prop_id = request.GET.get('propriedade')
    mes = request.GET.get('month')
    cat_id = request.GET.get('categoria')

    if prop_id:
        lancamentos = lancamentos.filter(propriedade_id=prop_id)
    if mes:
        try:
            ano, mes_num = mes.split('-')
            lancamentos = lancamentos.filter(data__year=ano, data__month=mes_num)
        except:
            pass
    if cat_id:
        lancamentos = lancamentos.filter(categoria_id=cat_id)

    total_recebido = lancamentos.filter(tipo__nome__iregex=r'^(Recebimento|Entrada)$').aggregate(Sum('valor'))['valor__sum'] or 0
    total_pago = lancamentos.filter(tipo__nome__iregex=r'^(Pagamento|Saída)$').aggregate(Sum('valor'))['valor__sum'] or 0
    saldo = total_recebido - total_pago

    context = {
        'lancamentos': lancamentos,
        'total_recebido': total_recebido,
        'total_pago': total_pago,
        'saldo': saldo,
        'propriedades': Propriedade.objects.all(),
        'categorias': Categoria.objects.all(),
    }
    return render(request, 'financeiro/relatorios.html', context)

@login_required
def exportar_pdf(request):
    lancamentos = Lancamento.objects.all().order_by('-data')
    prop_id = request.GET.get('propriedade')
    mes = request.GET.get('month')
    cat_id = request.GET.get('categoria')

    if prop_id:
        lancamentos = lancamentos.filter(propriedade_id=prop_id)
    if mes:
        try:
            ano, m = mes.split('-')
            lancamentos = lancamentos.filter(data__year=ano, data__month=m)
        except: pass
    if cat_id:
        lancamentos = lancamentos.filter(categoria_id=cat_id)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []
    styles = getSampleStyleSheet()
    
    style_body = ParagraphStyle('body', parent=styles['Normal'], fontSize=9, leading=11) 
    style_header = ParagraphStyle('header', parent=styles['Normal'], fontSize=10, leading=12, textColor=colors.whitesmoke, alignment=1, fontWeight='bold')

    try:
        logo = Image("logo_rd.jpg", width=1.8*inch, height=0.75*inch)
    except:
        logo = Paragraph("RD CONILON", styles['Normal'])

    fazenda_style = ParagraphStyle('FazendaTitle', parent=styles['Normal'], fontSize=32, textColor=colors.HexColor("#5d4037"), fontName='Helvetica-Bold', letterSpacing=2, alignment=0)

    header_data = [[logo, Paragraph("FAZENDA360", fazenda_style)]]
    header_table = Table(header_data, colWidths=[2.2*inch, 6.8*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('LEFTPADDING', (1,0), (1,0), 20),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(header_table)

    line_data = [['', '']]
    line_table = Table(line_data, colWidths=[9*inch, 0])
    line_table.setStyle(TableStyle([('LINEBELOW', (0,0), (0,0), 2, colors.HexColor("#5d4037")), ('BOTTOMPADDING', (0,0), (0,0), 8)]))
    elements.append(line_table)
    elements.append(Spacer(1, 0.2 * inch))

    total_recebido = lancamentos.filter(tipo__nome__iregex=r'^(Recebimento|Entrada)$').aggregate(Sum('valor'))['valor__sum'] or 0
    total_pago = lancamentos.filter(tipo__nome__iregex=r'^(Pagamento|Saída)$').aggregate(Sum('valor'))['valor__sum'] or 0
    saldo = total_recebido - total_pago
    
    def fmt(v): return f"R$ {v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    card_label_style = ParagraphStyle('CardLabel', parent=styles['Normal'], fontSize=10, textColor=colors.whitesmoke, alignment=1)
    card_text_style = ParagraphStyle('CardText', parent=styles['Normal'], fontSize=14, textColor=colors.white, alignment=1, fontName='Helvetica-Bold')

    dados_grafico_qs = lancamentos.filter(tipo__nome__iregex=r'^(Pagamento|Saída)$')\
                                  .values('categoria__nome')\
                                  .annotate(total=Sum('valor'))\
                                  .order_by('-total')[:10]
    
    resumo_inner_data = [
        [Paragraph("TOTAL RECEBIDO", card_label_style), Paragraph(fmt(total_recebido), card_text_style)],
        [Paragraph("TOTAL PAGO", card_label_style), Paragraph(fmt(total_pago), card_text_style)],
        [Paragraph("SALDO DO PERÍODO", card_label_style), Paragraph(fmt(saldo), card_text_style)]
    ]
    
    def criar_card_formatado(row, width):
        t_card = Table([row], colWidths=[width])
        label_text = row[0].text
        if "RECEBIDO" in label_text:
            bg = colors.HexColor("#2e7d32")
        elif "PAGO" in label_text:
            bg = colors.HexColor("#c62828")
        else:
            bg = colors.HexColor("#2e7d32") if saldo >= 0 else colors.HexColor("#c62828")
        
        t_card.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('ROUNDRECT', (0,0), (-1,-1), 5, 1, colors.white),
        ]))
        return t_card

    if dados_grafico_qs.exists():
        d = Drawing(320, 150)
        bc = VerticalBarChart()
        bc.x, bc.y = 45, 45
        bc.height, bc.width = 90, 260
        bc.data = [[float(item['total']) for item in dados_grafico_qs]]
        bc.strokeColor = colors.white
        bc.valueAxis.valueMin = 0
        bc.valueAxis.labels.fontSize = 7
        bc.categoryAxis.labels.fontSize = 7
        bc.categoryAxis.labels.angle = 30
        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.categoryAxis.categoryNames = [item['categoria__nome'] for item in dados_grafico_qs]
        
        rd_colors = [colors.HexColor("#5d4037"), colors.HexColor("#2e7d32"), colors.HexColor("#1565c0"), 
                     colors.HexColor("#fbc02d"), colors.HexColor("#e64a19"), colors.HexColor("#7b1fa2"),
                     colors.HexColor("#0097a7"), colors.HexColor("#689f38"), colors.HexColor("#ffa000"),
                     colors.HexColor("#455a64")]
        
        for i, color in enumerate(rd_colors):
            if i < len(bc.data[0]):
                bc.bars[(0, i)].fillColor = color
        
        d.add(bc)
        resumo_col_data = [[criar_card_formatado(row, 2.5*inch)] for row in resumo_inner_data]
        layout_table = Table([[d, Table(resumo_col_data, colWidths=[2.7*inch], rowHeights=42)]], colWidths=[4.8*inch, 4.2*inch])
        layout_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (0,0), (0,0), 'CENTER')]))
        elements.append(layout_table)
    else:
        resumo_row_data = [criar_card_formatado(row, 2.8*inch) for row in resumo_inner_data]
        layout_table = Table([resumo_row_data], colWidths=[3*inch, 3*inch, 3*inch])
        layout_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        elements.append(layout_table)

    elements.append(Spacer(1, 0.2 * inch))
    data = [[Paragraph(h, style_header) for h in ['DATA', 'PROPRIEDADE', 'CATEGORIA', 'TIPO', 'VALOR', 'DESCRIÇÃO']]]
    for l in lancamentos:
        val_f = f"{l.valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        data.append([
            Paragraph(l.data.strftime('%d/%m/%Y'), style_body),
            Paragraph(l.propriedade.nome, style_body),
            Paragraph(f"{l.categoria.nome} - {l.subcategoria.nome}", style_body),
            Paragraph(l.tipo.nome, style_body),
            Paragraph(f"R$ {val_f}", style_body),
            Paragraph(l.descricao or "-", style_body)
        ])

    total_str = f"{saldo:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    data.append(['', '', '', Paragraph('<b>SALDO FINAL:</b>', style_body), Paragraph(f'<b>R$ {total_str}</b>', style_body), ''])

    t = Table(data, colWidths=[0.8*inch, 1.6*inch, 1.8*inch, 0.9*inch, 1.2*inch, 3.3*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#5d4037")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.whitesmoke, colors.white]),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
    ]))
    elements.append(t)
    
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.grey, alignment=2)
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(f"Documento emitido pelo sistema FAZENDA360 em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", footer_style))

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    response['Content-Disposition'] = f'attachment; filename="Relatorio_Fazenda360_{timestamp}.pdf"'
    return response

@login_required
def remover_lancamento(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        try:
            lancamento = Lancamento.objects.get(id=id)
            lancamento.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método inválido'})

@login_required
def remover_propriedade(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        try:
            prop = Propriedade.objects.get(id=id)
            prop.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método inválido'})

@login_required
def remover_categoria(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        try:
            cat = Categoria.objects.get(id=id)
            cat.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método inválido'})

@login_required
def remover_subcategoria(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        try:
            subcat = Subcategoria.objects.get(id=id)
            subcat.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método inválido'})
