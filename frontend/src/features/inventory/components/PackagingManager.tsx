
import { useState } from 'react'
import { Plus, Package } from 'lucide-react'

import { useProducts } from '../../products/hooks/useProducts'
import { useCreateProductPackaging } from '../hooks/useInventory'

export default function PackagingManager() {
  const { data, isLoading } = useProducts()
  const createPackaging = useCreateProductPackaging()

  const [product, setProduct] = useState('')
  const [name, setName] = useState('')
  const [conversionFactor, setConversionFactor] = useState('1')
  const [purchaseEnabled, setPurchaseEnabled] = useState(true)
  const [salesEnabled, setSalesEnabled] = useState(true)

  const products = data?.results ?? []

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!product || !name.trim() || Number(conversionFactor) < 1) {
      return
    }

    try {
      await createPackaging.mutateAsync({
        product: Number(product),
        name: name.trim(),
        conversion_factor: Number(conversionFactor),
        purchase_enabled: purchaseEnabled,
        sales_enabled: salesEnabled,
        is_active: true,
      })

      setName('')
      setConversionFactor('1')
      setPurchaseEnabled(true)
      setSalesEnabled(true)
    } catch {
      // The mutation error is displayed below.
    }
  }

  return (
    <section className="packaging-manager">
      <div className="section-heading">
        <div>
          <h2>Product Packaging</h2>
          <p>Configure package sizes used when purchasing and selling stock.</p>
        </div>
        <Package size={22} />
      </div>

      <form onSubmit={handleSubmit} className="packaging-form">
        <label>
          Product
          <select
            value={product}
            onChange={(event) => setProduct(event.target.value)}
            required
          >
            <option value="">
              {isLoading ? 'Loading products...' : 'Select product'}
            </option>
            {products.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name} ({item.sku})
              </option>
            ))}
          </select>
        </label>

        <label>
          Packaging name
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="e.g. Bottle, Carton, Pack"
            required
          />
        </label>

        <label>
          Base units per package
          <input
            type="number"
            min="1"
            step="1"
            value={conversionFactor}
            onChange={(event) => setConversionFactor(event.target.value)}
            required
          />
        </label>

        <div className="packaging-options">
          <label>
            <input
              type="checkbox"
              checked={purchaseEnabled}
              onChange={(event) => setPurchaseEnabled(event.target.checked)}
            />
            Enable for purchasing
          </label>

          <label>
            <input
              type="checkbox"
              checked={salesEnabled}
              onChange={(event) => setSalesEnabled(event.target.checked)}
            />
            Enable for selling
          </label>
        </div>

        <button
          type="submit"
          disabled={createPackaging.isPending || !product}
        >
          <Plus size={17} />
          {createPackaging.isPending ? 'Saving...' : 'Add Packaging'}
        </button>

        {createPackaging.isError && (
          <p className="form-error">
            {(createPackaging.error as Error).message ||
              'Could not create packaging. Please try again.'}
          </p>
        )}

        {createPackaging.isSuccess && (
          <p className="form-success">Packaging created successfully.</p>
        )}
      </form>
    </section>
  )
}
