import { KTPData } from '../types/ktp'

interface KTPDisplayProps {
  data: KTPData
  onReset: () => void
}

export default function KTPDisplay({ data, onReset }: KTPDisplayProps) {
  const fieldLabels = {
    nik: 'NIK',
    name: 'Nama',
    birth_place: 'Tempat Lahir',
    birth_date: 'Tanggal Lahir',
    gender: 'Jenis Kelamin',
    address: 'Alamat',
    blood_type: 'Golongan Darah',
    religion: 'Agama',
    marital_status: 'Status Perkawinan',
    occupation: 'Pekerjaan',
    nationality: 'Kewarganegaraan',
    valid_until: 'Berlaku Hingga'
  }

  return (
    <div className="space-y-6">
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Hasil Ekstraksi KTP
          </h3>
        </div>
        <div className="border-t border-gray-200">
          <dl>
            {Object.entries(fieldLabels).map(([key, label], index) => {
              const value = data[key as keyof KTPData]
              if (!value) return null

              return (
                <div key={key} className={`px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6 ${
                  index % 2 === 0 ? 'bg-gray-50' : 'bg-white'
                }`}>
                  <dt className="text-sm font-medium text-gray-500">{label}</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                    {value}
                  </dd>
                </div>
              )
            })}
          </dl>
        </div>
      </div>
      
      <div className="flex justify-center">
        <button
          onClick={onReset}
          className="btn-primary"
        >
          Proses KTP Lain
        </button>
      </div>
    </div>
  )
}