
import { useState } from 'react'
import { isAxiosError } from 'axios'
import { X } from 'lucide-react'

import {
  useCategories,
  useCreateProduct,
  useProductFamilies,
} from '../hooks/useProducts'

import type { CreateProductPayload } from '../product-catalog.types'

interface ProductFormProps {
  onClose: () => void
}

const initialForm = {
  name: '',
  product_family: '',
  category: '',
  brand: '',
  size_value: '',
  size_unit: 'G' as CreateProductPayload['size_unit'],
  base_unit: '',
  retail_price: '',
  wholesale_price: '',
  wholesale_min_quantity: '1',
  reorder_level: '0',
}

export default function ProductForm({ onClose }: ProductFormProps) {
  const [form, setForm] = useState(initialForm)
  const [errorMessage, setErrorMessage] = useState('')

  const { data: categoriesData, isLoading: loadingCategories } = useCategories()
  const { data: familiesData, isLoading: loadingFamilies } = useProductFamilies()
  const createProduct = useCreateProduct()

  const categories = categoriesData?.results.filter(
    (category) => category.is_active,
  ) ?? []

  const families = familiesData?.results ?? []

  function updateField(field: keyof typeof initialForm, value: string) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }))
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setErrorMessage('')

    const payload: CreateProductPayload = {
      name: form.name.trim(),
      product_family: Number(form.product_family),
      category: Number(form.category),
      brand: form.brand.trim(),
      size_value: form.size_value,
      size_unit: form.size_unit,
      base_unit: form.base_unit.trim(),
      retail_price: form.retail_price,
      wholesale_price: form.wholesale_price,
      wholesale_min_quantity: Number(form.wholesale_min_quantity),
      reorder_level: Number(form.reorder_level),
      is_active: true,
    }

    try {
      await createProduct.mutateAsync(payload)
      onClose()
    } catch (error) {
      if (isAxiosError(error)) {
        const detail = error.response?.data

        if (typeof detail === 'string') {
          setErrorMessage(detail)
        } else if (detail && typeof detail === 'object') {
          setErrorMessage(
            Object.entries(detail)
              .map(([field, messages]) =>
                `${field}: ${Array.isArray(messages) ? messages.join(', ') : String(messages)}`,
              )
              .join(' | '),
          )
        } else {
          setErrorMessage('Unable to create product. Please try again.')
        }
      } else {
        setErrorMessage('An unexpected error occurred.')
      }
    }
  }

  const loadingOptions = loadingCategories || loadingFamilies

  return (
    <div className="product-modal-backdrop">
      <div
        className="product-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="product-form-title"
      >
        <div className="product-modal-header">
          <div>
            <span className="page-eyebrow">PRODUCT CATALOGUE</span>
            <h2 id="product-form-title">Add New Product</h2>
            <p>Enter the product details below.</p>
          </div>

          <button
            type="button"
            className="product-modal-close"
            onClick={onClose}
            aria-label="Close form"
          >
            <X size={20} />
          </button>
        </div>

        {loadingOptions ? (
          <div className="products-message">
            Loading categories and product families...
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="product-form-grid">
              <label>
                Product Name *
                <input
                  required
                  maxLength={150}
                  value={form.name}
                  onChange={(event) => updateField('name', event.target.value)}
                  placeholder="e.g. Blue Band Margarine"
                />
              </label>

              <label>
                Product Family *
                <select
                  required
                  value={form.product_family}
                  onChange={(event) =>
                    updateField('product_family', event.target.value)
                  }
                >
                  <option value="">Select product family</option>
                  {families.map((family) => (
                    <option key={family.id} value={family.id}>
                      {family.name} ({family.sku_prefix})
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Category *
                <select
                  required
                  value={form.category}
                  onChange={(event) =>
                    updateField('category', event.target.value)
                  }
                >
                  <option value="">Select category</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Brand
                <input
                  maxLength={100}
                  value={form.brand}
                  onChange={(event) => updateField('brand', event.target.value)}
                  placeholder="e.g. Blue Band"
                />
              </label>

              <label>
                Size *
                <input
                  type="number"
                  required
                  min="0.001"
                  step="0.001"
                  value={form.size_value}
                  onChange={(event) =>
                    updateField('size_value', event.target.value)
                  }
                  placeholder="e.g. 500"
                />
              </label>

              <label>
                Size Unit *
                <select
                  value={form.size_unit}
                  onChange={(event) =>
                    updateField(
                      'size_unit',
                      event.target.value as CreateProductPayload['size_unit'],
                    )
                  }
                >
                  <option value="G">Grams (G)</option>
                  <option value="KG">Kilograms (KG)</option>
                  <option value="ML">Millilitres (ML)</option>
                  <option value="L">Litres (L)</option>
                </select>
              </label>

              <label>
                Base Unit *
                <input
                  required
                  maxLength={30}
                  value={form.base_unit}
                  onChange={(event) =>
                    updateField('base_unit', event.target.value)
                  }
                  placeholder="e.g. PIECE, BOTTLE, PACK"
                />
              </label>

              <label>
                Reorder Level *
                <input
                  type="number"
                  required
                  min="0"
                  step="1"
                  value={form.reorder_level}
                  onChange={(event) =>
                    updateField('reorder_level', event.target.value)
                  }
                />
              </label>

              <label>
                Retail Price (KES) *
                <input
                  type="number"
                  required
                  min="0"
                  step="0.01"
                  value={form.retail_price}
                  onChange={(event) =>
                    updateField('retail_price', event.target.value)
                  }
                  placeholder="0.00"
                />
              </label>

              <label>
                Wholesale Price (KES) *
                <input
                  type="number"
                  required
                  min="0"
                  step="0.01"
                  value={form.wholesale_price}
                  onChange={(event) =>
                    updateField('wholesale_price', event.target.value)
                  }
                  placeholder="0.00"
                />
              </label>

              <label>
                Minimum Wholesale Quantity *
                <input
                  type="number"
                  required
                  min="1"
                  step="1"
                  value={form.wholesale_min_quantity}
                  onChange={(event) =>
                    updateField('wholesale_min_quantity', event.target.value)
                  }
                  placeholder="e.g. 12"
                />
                <small>
                  Minimum number of {form.base_unit.trim() || 'base units'} required for wholesale pricing.
                </small>
              </label>
            </div>

            {families.length === 0 && (
              <p className="product-form-warning">
                No product families exist yet. Create a product family before
                adding products.
              </p>
            )}

            {categories.length === 0 && (
              <p className="product-form-warning">
                No active categories exist yet. Create a category before
                adding products.
              </p>
            )}

            {errorMessage && (
              <div className="product-form-error">
                {errorMessage}
              </div>
            )}

            <div className="product-form-actions">
              <button
                type="button"
                className="product-cancel-button"
                onClick={onClose}
                disabled={createProduct.isPending}
              >
                Cancel
              </button>

              <button
                type="submit"
                className="primary-button"
                disabled={
                  createProduct.isPending ||
                  loadingOptions ||
                  categories.length === 0 ||
                  families.length === 0
                }
              >
                {createProduct.isPending ? 'Saving...' : 'Save Product'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
