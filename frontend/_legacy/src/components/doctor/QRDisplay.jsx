// frontend/src/components/doctor/QRDisplay.jsx
import { useState } from 'react';
import { QRCodeSVG } from 'qrcode.react';

const QRDisplay = ({ doctorId, doctorName }) => {
  const [qrValue] = useState(JSON.stringify({
    type: 'doctor',
    id: doctorId,
    name: doctorName,
    clinic: 'Ubuntu Campus Clinic',
    url: `${window.location.origin}/book?doctor=${doctorId}`
  }));

  const downloadQR = () => {
    const svg = document.getElementById('doctor-qr-code');
    const svgData = new XMLSerializer().serializeToString(svg);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);
      const pngFile = canvas.toDataURL('image/png');
      const downloadLink = document.createElement('a');
      downloadLink.download = `doctor-${doctorId}-qr.png`;
      downloadLink.href = pngFile;
      downloadLink.click();
    };
    
    img.src = 'data:image/svg+xml;base64,' + btoa(svgData);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="text-center">
        <h2 className="text-lg font-semibold text-gray-800 mb-2">Doctor QR Code</h2>
        <p className="text-gray-500 text-sm mb-6">
          Patients can scan this QR code to book appointments with you
        </p>

        <div className="flex justify-center mb-6">
          <div className="p-4 bg-white rounded-xl shadow-lg">
            <QRCodeSVG
              id="doctor-qr-code"
              value={qrValue}
              size={250}
              level="H"
              includeMargin={true}
            />
          </div>
        </div>

        <div className="mb-6">
          <p className="text-gray-800 font-medium">{doctorName}</p>
          <p className="text-gray-500 text-sm">ID: {doctorId}</p>
        </div>

        <div className="flex gap-3 justify-center">
          <button
            onClick={downloadQR}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download QR Code
          </button>
        </div>

        <div className="mt-6 p-3 bg-gray-50 rounded-lg text-left">
          <p className="text-sm text-gray-600">
            <strong>📱 How to use:</strong>
          </p>
          <ul className="text-sm text-gray-500 mt-2 space-y-1 list-disc list-inside">
            <li>Display this QR code in your office</li>
            <li>Patients can scan with their phone camera</li>
            <li>They will be directed to book an appointment with you</li>
            <li>You can also print this code and place it on your door</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default QRDisplay;