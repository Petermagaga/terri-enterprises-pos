
import jsPDF from 'jspdf'

import type { Sale } from '../sales.types'
import type { ProductPackaging } from '../../inventory/packaging.types'
import type { Product } from '../../products/product.types'

interface InvoiceCartItem {
  product: Product
  packaging: ProductPackaging | null
  pricingType: 'RETAIL' | 'WHOLESALE'
  quantity: number
  unitPrice: number
  packagePrice: number
  total: number
}

interface PdfLineItem {
  description: string
  sku: string
  quantity: number
  unit: string
  unitPrice: number
  total: number
  pricingType: string
}

const BUSINESS_NAME = 'Terri Enterprises'
const CURRENCY = 'KES'
const PAGE_WIDTH = 210
const PAGE_HEIGHT = 297
const LEFT = 14
const RIGHT = 196
const CONTENT_WIDTH = RIGHT - LEFT

function money(value: number | string): string {
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: CURRENCY,
    minimumFractionDigits: 2,
  }).format(Number(value) || 0)
}

function dateTime(value: string | Date): string {
  return new Intl.DateTimeFormat('en-KE', {
    dateStyle: 'medium',
    timeStyle: 'short',
    timeZone: 'Africa/Nairobi',
  }).format(new Date(value))
}

function dateReference(prefix: string): string {
  const now = new Date()
  const date = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Africa/Nairobi',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(now).replaceAll('-', '')

  const time = new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Africa/Nairobi',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hourCycle: 'h23',
  }).format(now).replaceAll(':', '')

  return `${prefix}-${date}-${time}`
}

async function loadLogo(): Promise<string | null> {
  try {
    const response = await fetch('/terri-logo.png')

    if (!response.ok) return null

    const blob = await response.blob()

    return await new Promise((resolve) => {
      const reader = new FileReader()

      reader.onload = () => {
        resolve(typeof reader.result === 'string' ? reader.result : null)
      }

      reader.onerror = () => resolve(null)
      reader.readAsDataURL(blob)
    })
  } catch {
    return null
  }
}

async function createPdf(): Promise<jsPDF> {
  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
  })

  const logo = await loadLogo()

  if (logo) {
    try {
      doc.addImage(logo, 'PNG', LEFT, 10, 25, 25)
    } catch {
      // Continue without the logo if the image cannot be rendered.
    }
  }

  doc.setTextColor(35, 55, 45)
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(19)
  doc.text(BUSINESS_NAME, 45, 19)

  doc.setFont('helvetica', 'normal')
  doc.setFontSize(9)
  doc.setTextColor(100, 100, 100)
  doc.text('Management System', 45, 25)

  doc.setDrawColor(35, 110, 75)
  doc.setLineWidth(0.8)
  doc.line(LEFT, 40, RIGHT, 40)

  return doc
}

function addDocumentHeading(
  doc: jsPDF,
  heading: string,
  reference: string,
  createdAt: string | Date,
): number {
  doc.setTextColor(35, 55, 45)
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(16)
  doc.text(heading, LEFT, 51)

  doc.setFont('helvetica', 'normal')
  doc.setFontSize(9)
  doc.setTextColor(70, 70, 70)

  doc.text(`Reference: ${reference}`, LEFT, 59)
  doc.text(`Date: ${dateTime(createdAt)}`, LEFT, 65)

  return 76
}

function drawTableHeader(doc: jsPDF, y: number): number {
  doc.setFillColor(35, 110, 75)
  doc.rect(LEFT, y, CONTENT_WIDTH, 9, 'F')

  doc.setFont('helvetica', 'bold')
  doc.setFontSize(8)
  doc.setTextColor(255, 255, 255)

  doc.text('Description', LEFT + 2, y + 6)
  doc.text('Qty', 119, y + 6, { align: 'right' })
  doc.text('Unit Price', 153, y + 6, { align: 'right' })
  doc.text('Total', RIGHT - 2, y + 6, { align: 'right' })

  return y + 9
}

function drawLineItems(
  doc: jsPDF,
  items: PdfLineItem[],
  startY: number,
): number {
  let y = drawTableHeader(doc, startY)

  items.forEach((item, index) => {
    const description = doc.splitTextToSize(
      `${item.description}\nSKU: ${item.sku} | ${item.unit} | ${item.pricingType}`,

      88,
    )

    const rowHeight = Math.max(12, description.length * 4 + 3)

    if (y + rowHeight > PAGE_HEIGHT - 30) {
      doc.addPage()
      y = 18
      y = drawTableHeader(doc, y)
    }

    if (index % 2 === 0) {
      doc.setFillColor(245, 248, 246)
      doc.rect(LEFT, y, CONTENT_WIDTH, rowHeight, 'F')
    }

    doc.setFont('helvetica', 'normal')
    doc.setFontSize(8)
    doc.setTextColor(45, 45, 45)

    doc.text(description, LEFT + 2, y + 5)
    doc.text(String(item.quantity), 119, y + 5, { align: 'right' })
    doc.text(money(item.unitPrice), 153, y + 5, { align: 'right' })
    doc.text(money(item.total), RIGHT - 2, y + 5, { align: 'right' })

    doc.setDrawColor(225, 230, 226)
    doc.line(LEFT, y + rowHeight, RIGHT, y + rowHeight)

    y += rowHeight
  })

  return y + 5
}

function drawTotal(
  doc: jsPDF,
  y: number,
  total: number | string,
): number {
  if (y > PAGE_HEIGHT - 35) {
    doc.addPage()
    y = 25
  }

  doc.setDrawColor(35, 110, 75)
  doc.setLineWidth(0.5)
  doc.line(120, y, RIGHT, y)

  doc.setFont('helvetica', 'bold')
  doc.setFontSize(11)
  doc.setTextColor(35, 55, 45)

  doc.text('TOTAL', 122, y + 8)
  doc.text(money(total), RIGHT - 2, y + 8, { align: 'right' })

  return y + 15
}

function drawFooter(doc: jsPDF): void {
  const pageCount = doc.getNumberOfPages()

  for (let page = 1; page <= pageCount; page += 1) {
    doc.setPage(page)

    doc.setFont('helvetica', 'normal')
    doc.setFontSize(8)
    doc.setTextColor(120, 120, 120)

    doc.text(
      'Thank you for shopping with Terri Enterprises.',
      PAGE_WIDTH / 2,
      PAGE_HEIGHT - 12,
      { align: 'center' },
    )

    doc.text(
      `Page ${page} of ${pageCount}`,
      RIGHT,
      PAGE_HEIGHT - 6,
      { align: 'right' },
    )
  }
}

function savePdf(doc: jsPDF, filename: string): void {
  drawFooter(doc)
  doc.save(filename)
}

function invoiceItems(items: InvoiceCartItem[]): PdfLineItem[] {
  return items.map((item) => ({
    description: item.product.name,
    sku: item.product.sku,
    quantity: item.quantity,
    unit: item.packaging?.name || item.product.base_unit,
    unitPrice: item.packagePrice,
    total: item.total,
    pricingType: item.pricingType,
  }))
}

function receiptItems(sale: Sale): PdfLineItem[] {
  return sale.items.map((item) => ({
    description: item.product_name_snapshot,
    sku: item.product_sku_snapshot,
    quantity: Number(item.quantity),
    unit: item.packaging_name_snapshot || item.base_unit_snapshot,
    unitPrice: Number(item.selling_price_per_package),
    total: Number(item.total_amount),
    pricingType: item.pricing_type,
  }))
}

export async function downloadInvoicePdf(
  items: InvoiceCartItem[],
): Promise<void> {
  if (items.length === 0) {
    throw new Error('Add items to the cart before generating an invoice.')
  }

  const doc = await createPdf()
  const reference = dateReference('INV')
  const total = items.reduce((sum, item) => sum + item.total, 0)

  const y = addDocumentHeading(
    doc,
    'SALES INVOICE',
    reference,
    new Date(),
  )

  let nextY = drawLineItems(doc, invoiceItems(items), y)
  nextY = drawTotal(doc, nextY, total)

  doc.setFont('helvetica', 'italic')
  doc.setFontSize(8)
  doc.setTextColor(100, 100, 100)
  doc.text(
    'This invoice is based on the current cart and is not proof of payment.',
    LEFT,
    nextY + 3,
  )

  savePdf(doc, `${reference}.pdf`)
}

export async function downloadReceiptPdf(sale: Sale): Promise<void> {
  if (sale.status !== 'COMPLETED' || !sale.receipt_number) {
    throw new Error('A receipt is only available for completed sales.')
  }

  const doc = await createPdf()

  let y = addDocumentHeading(
    doc,
    'PAYMENT RECEIPT',
    sale.receipt_number,
    sale.completed_at || sale.created_at,
  )

  y = drawLineItems(doc, receiptItems(sale), y)
  y = drawTotal(doc, y, sale.total_amount)

  if (y > PAGE_HEIGHT - 65) {
    doc.addPage()
    y = 20
  }

  doc.setFont('helvetica', 'bold')
  doc.setFontSize(10)
  doc.setTextColor(35, 55, 45)
  doc.text('PAYMENTS RECEIVED', LEFT, y + 5)

  y += 12

  doc.setFont('helvetica', 'normal')
  doc.setFontSize(8)
  doc.setTextColor(45, 45, 45)

  sale.payments.forEach((payment) => {
    if (y > PAGE_HEIGHT - 25) {
      doc.addPage()
      y = 20
    }

    const method = payment.payment_method === 'MPESA'
      ? `M-Pesa${payment.reference ? ` (${payment.reference})` : ''}`
      : 'Cash'

    doc.text(method, LEFT + 2, y)
    doc.text(money(payment.amount), RIGHT - 2, y, { align: 'right' })

    y += 7
  })

  doc.setFont('helvetica', 'bold')
  doc.text(
    `Total paid: ${money(
      sale.payments.reduce(
        (sum, payment) => sum + Number(payment.amount),
        0,
      ),
    )}`,
    RIGHT - 2,
    y + 3,
    { align: 'right' },
  )

  y += 13

  doc.setFont('helvetica', 'normal')
  doc.setFontSize(8)
  doc.setTextColor(100, 100, 100)
  doc.text(
    `Served by: ${sale.processed_by_name?.trim() || `User #${sale.processed_by}`}`,
    LEFT,
    y,
  )

  savePdf(doc, `${sale.receipt_number}.pdf`)
}
