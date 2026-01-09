import os
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib import colors
from reportlab.lib.units import cm

KOP_SURAT = """
<b><font size="12">BADAN METEOROLOGI, KLIMATOLOGI, DAN GEOFISIKA</font></b><br/>
<font size="10">
BALAI BESAR METEOROLOGI, KLIMATOLOGI, DAN GEOFISIKA WILAYAH IV<br/>
LABORATORIUM KALIBRASI BBMKG WILAYAH IV MAKASSAR
</font><br/>
Jl. Prof. Abdurrahman Basalamah No. 4, Panaikang, Makassar, Kode Pos 90231<br/>
Telp. (0411) 456493, 437331 Website : http://bbmkg4.com,
Email address : inskal.bbmkg4@bmkg.go.id
"""

#GENERATE PDF
def generate_pdf(
    output_path: str,
    logo_path: str,
    nama: str,
    nip: str,
    instansi: str,
    kegiatan: str,
    periode: str,
    kota: str,
    tanggal_str: str,
    ttd_io
):
   
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    elements = []

#Style
    isi_style = ParagraphStyle(
        "isi",
        parent=styles["Normal"],
        fontSize=11,
        leading=13,
        alignment=TA_JUSTIFY
    )

    label_style = ParagraphStyle(
        "label",
        parent=styles["Normal"],
        fontSize=11,
        leading=13,
        alignment=TA_LEFT
    )

    colon_style = ParagraphStyle(
        "colon",
        parent=styles["Normal"],
        fontSize=11,
        leading=13,
        alignment=TA_LEFT
    )

    address_style = ParagraphStyle(
        "alamat",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        alignment=TA_CENTER
    )

    #TABEL
    data_table = Table(
        [
            [Paragraph("Nama", label_style), Paragraph(":", colon_style), Paragraph(nama, isi_style)],
            [Paragraph("NIP / NIK", label_style), Paragraph(":", colon_style), Paragraph(nip, isi_style)],
            [Paragraph("Instansi", label_style), Paragraph(":", colon_style), Paragraph(instansi, isi_style)],
            [Paragraph("Nama Kegiatan/Pekerjaan", label_style), Paragraph(":", colon_style), Paragraph(kegiatan, isi_style)],
            [Paragraph("Periode Penugasan", label_style), Paragraph(":", colon_style), Paragraph(periode, isi_style)],
        ],
        colWidths=[5 * cm, 0.4 * cm, 10.3 * cm]
    )

    data_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))

    #KOP SURAT
    kop_table = Table(
        [
            [
                Image(logo_path, 1.9 * cm, 2.3 * cm),
                Paragraph(KOP_SURAT.strip(), address_style)
            ]
        ],
        colWidths=[2.3 * cm, 14.7 * cm]
    )

    kop_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("LINEAFTER", (0, 0), (0, 0), 1, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
        ("ALIGN", (1, 0), (1, 0), "CENTER"),
    ]))

    #ISI SURAT
    elements.extend([
        kop_table,
        Spacer(1, 11),
        Paragraph(
            "<b>SURAT PERNYATAAN MENJAGA KERAHASIAAN INFORMASI</b>",
            ParagraphStyle("judul", alignment=TA_CENTER, fontSize=12)
        ),
        Spacer(1, 11),
        Paragraph("Saya yang bertanda tangan dibawah ini:", isi_style),
        Spacer(1, 11),
        data_table,
        Spacer(1, 11),
        Paragraph("""
        Dengan ini menyatakan hal-hal sebagai berikut:<br/><br/>
        1. Tunduk dan patuh kepada seluruh ketentuan yang terkait pengelolaan barang dan/atau jasa informasi dan pengamanan teknologi informasi yang berlaku di Balai Besar Meteorologi Klimatologi dan Geofisika Wilayah IV Makassar;<br/><br/>
        2. Selalu menjaga Informasi Rahasia milik Balai Besar Meteorologi Klimatologi dan Geofisika Wilayah IV Makassar sesuai ketentuan dan prosedur yang berlaku;<br/><br/>
        3. Tidak mengungkap, menyalin, memperbanyak, atau meminjamkan Informasi Rahasia untuk maksud apapun di luar tugas dan tanggung jawab saya selama penugasan di Balai Besar Meteorologi Klimatologi dan Geofisika Wilayah IV Makassar;<br/><br/>
        4. Tidak menyalahgunakan wewenang atas akses dokumen dan sistem informasi yang terdapat di Balai Besar Meteorologi Klimatologi dan Geofisika Wilayah IV Makassar;<br/><br/>
        5. Tidak memberikan User ID dan Password saya kepada pihak lain; dan<br/><br/>
        6. Apabila terbukti bahwa saya melakukan pelanggaran atas perihal yang telah dinyatakan dalam surat ini, maka saya bersedia dikenakan sanksi sesuai dengan peraturan yang berlaku.<br/><br/>
        Pernyataan ini tetap berlaku walaupun penugasan saya di Balai Besar Meteorologi Klimatologi dan Geofisika Wilayah IV Makassar telah berakhir.<br/><br/>
        Demikian, Surat Pernyataan ini saya buat dalam keadaan sadar dan tanpa paksaan dari pihak manapun.
        """, isi_style),
        Spacer(1, 11),
        Table([
            [Paragraph(f"{kota}, {tanggal_str}", isi_style)],
            [Paragraph("Yang menyatakan,", isi_style)],
            [Image(ttd_io, 3 * cm, 2 * cm)],
            [Paragraph(nama, isi_style)]
        ])
    ])

    doc.build(elements)
