
import { Suspense } from 'react'
import { RouterProvider } from 'react-router-dom'
import { router } from './app/router'

function App() {
  return (
    <Suspense
      fallback={
        <div style={{ padding: '24px', textAlign: 'center' }}>
          Loading page...
        </div>
      }
    >
      <RouterProvider router={router} />
    </Suspense>
  )
}

export default App
