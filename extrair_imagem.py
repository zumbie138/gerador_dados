import pymupdf

doc = pymupdf.open('extrair_imagem.pdf')

pag = doc[0]

lista_imagens = pag.get_images()

if lista_imagens:
    xref = lista_imagens[0][0]
    
    pix = pymupdf.Pixmap(doc, xref)

    pix.save('jbs_icone.png')

doc.close()