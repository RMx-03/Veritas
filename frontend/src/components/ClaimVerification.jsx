import { CheckCircle, XCircle, AlertTriangle, Info } from 'lucide-react'

function ClaimVerification({ claims }) {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'verified':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'false':
        return <XCircle className="h-5 w-5 text-red-500" />
      case 'misleading':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />
      default:
        return <Info className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'verified':
        return 'bg-green-50 border-green-200'
      case 'false':
        return 'bg-red-50 border-red-200'
      case 'misleading':
        return 'bg-yellow-50 border-yellow-200'
      default:
        return 'bg-gray-50 border-gray-200'
    }
  }

  return (
    <div className="card">
      <h3 className="font-semibold text-gray-900 mb-4">Claim Verification</h3>
      
      {claims && claims.length > 0 ? (
        <div className="space-y-4">
          {claims.map((claim, index) => (
            <div
              key={index}
              className={`border rounded-lg p-4 ${getStatusColor(claim.status)}`}
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-0.5">
                  {getStatusIcon(claim.status)}
                </div>
                <div className="flex-1">
                  <div className="font-medium text-gray-900 mb-1">
                    "{claim.claim}"
                  </div>
                  <div className="text-sm text-gray-700 mb-2">
                    {claim.explanation}
                  </div>
                  {claim.source && (
                    <div className="text-xs text-gray-500">
                      Source: {claim.source}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <Info className="h-8 w-8 mx-auto mb-2" />
          <p>No health claims found on this label</p>
        </div>
      )}
    </div>
  )
}

export default ClaimVerification
