
import { useState } from 'react'
import { isAxiosError } from 'axios'

import { useCreatePurchase } from '../hooks/useInventory'
import { useSuppliers } from '../../suppliers/hooks/useSuppliers'

interface PurchaseFormProps {
  onClose: () => void
  onSuccess: (purchaseId: number) => void
}

export default function PurchaseForm({
  onClose,
  onSuccess,
}: PurchaseFormProps) {
  const [supplier, setSupplier] = useState('')
  const [supplierReference, setSupplierReference] = useState('')
  const [purchaseDate, setPurchaseDate] = useState(
    new Date().toISOString().slice(0, 10),
  )
  const [transportCost, setTransportCost] = useState('0.00')
  const [errorMessage, setErrorMessage] = useState('')

  const createPurchaseMutation = useCreatePurchase()
  const { data: suppliersData, isLoading: isLoadingSuppliers } = useSuppliers()

  const suppliers = suppliersData?.results ?? []

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setErrorMessage('')

    try {
      const purchase = await createPurchaseMutation.mutateAsync({
        supplier: Number(supplier),
        supplier_reference: supplierReference.trim(),
        purchase_date: purchaseDate,
        transport_cost: transportCost,
      })

      onSuccess(purchase.id)
    } catch (error) {
      if (isAxiosError(error)) {
        setErrorMessage(
          error.response?.data?.detail ??
            'Unable to create the purchase. Please check the details.',
        )
      } else {
        setErrorMessage('Something went wrong. Please try again.')
      }
    }
  }

  return (
    <div className="modal-overlay">
      <div className="product-form-modal">
        <div className="product-form-header">
          <div>
            <span className="page-eyebrow">INVENTORY MANAGEMENT</span>
            <h2>New Purchase</h2>
          </div>

          <button
            type="button"
            className="modal-close-button"
            onClick={onClose}
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="product-form">
          <label>
            Supplier
            <select
              value={supplier}
              onChange={(event) => setSupplier(event.target.value)}
              required
              disabled={isLoadingSuppliers}
            >
              <option value="">Select supplier</option>
              {suppliers
                .filter((item) => item.is_active)
                .map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
            </select>
          </label>

          <label>
            Supplier Invoice / Reference
            <input
              value={supplierReference}
              onChange={(event) => setSupplierReference(event.target.value)}
              placeholder="e.g. INV-00125"
            />
          </label>

          <label>
            Purchase Date
            <input
              type="date"
              value={purchaseDate}
              onChange={(event) => setPurchaseDate(event.target.value)}
              required
            />
          </label>

          <label>
            Transport Cost (KSh)
            <input
              type="number"
              min="0"
              step="0.01"
              value={transportCost}
              onChange={(event) => setTransportCost(event.target.value)}
              required
            />
          </label>

          {errorMessage && (
            <div className="form-error">{errorMessage}</div>
          )}

          <div className="product-form-actions">
            <button
              type="button"
              className="button-secondary"
              onClick={onClose}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="button-primary"
              disabled={createPurchaseMutation.isPending || !supplier}
            >
              {createPurchaseMutation.isPending
                ? 'Creating...'
                : 'Create Purchase'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
