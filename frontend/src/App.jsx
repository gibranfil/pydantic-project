import { useEffect, useState } from 'react'
import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:8000'

function App() {
  const [datasets, setDatasets] = useState([])
  const [selectedDataset, setSelectedDataset] = useState('')
  const [profile, setProfile] = useState(null)
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Upload a CSV file to begin exploring your data.' },
  ])
  const [draft, setDraft] = useState('')
  const [loading, setLoading] = useState(false)

  const loadDatasets = async () => {
    const response = await axios.get(`${API_BASE_URL}/datasets`)
    setDatasets(response.data.datasets || [])
    if (!selectedDataset && response.data.datasets?.length) {
      setSelectedDataset(response.data.datasets[0])
    }
  }

  const loadProfile = async (datasetName) => {
    if (!datasetName) return
    const response = await axios.get(`${API_BASE_URL}/datasets/${encodeURIComponent(datasetName)}`)
    setProfile(response.data.profile)
  }

  useEffect(() => {
    loadDatasets()
  }, [])

  useEffect(() => {
    if (selectedDataset) {
      loadProfile(selectedDataset)
    }
  }, [selectedDataset])

  const handleUpload = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    const nextDataset = response.data.dataset
    setSelectedDataset(nextDataset)
    setMessages((current) => [
      ...current,
      { role: 'assistant', content: `Loaded ${nextDataset}.` },
    ])
    await loadDatasets()
  }

  const handleSend = async (event) => {
    event.preventDefault()
    if (!draft.trim()) return

    const message = draft.trim()
    setDraft('')
    setMessages((current) => [...current, { role: 'user', content: message }])
    setLoading(true)

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message,
        dataset: selectedDataset || null,
      })

      setMessages((current) => [...current, { role: 'assistant', content: response.data.answer }])
    } catch (error) {
      setMessages((current) => [...current, { role: 'assistant', content: 'Could not reach the backend.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <header>
        <h1>AI Data Analyst Assistant</h1>
        <p>Developer UI v1 for uploading CSVs, inspecting profiles, and chatting with the assistant.</p>
      </header>

      <section className="panel upload-panel">
        <label htmlFor="csv-upload">Upload dataset</label>
        <input id="csv-upload" type="file" accept=".csv" onChange={handleUpload} />
      </section>

      <section className="panel">
        <h2>Uploaded datasets</h2>
        <ul>
          {datasets.map((dataset) => (
            <li key={dataset} className={dataset === selectedDataset ? 'active' : ''} onClick={() => setSelectedDataset(dataset)}>
              {dataset}
            </li>
          ))}
        </ul>
      </section>

      <section className="panel">
        <h2>Dataset profile</h2>
        {profile ? (
          <div className="profile-grid">
            <div><strong>Rows</strong><span>{profile.rows}</span></div>
            <div><strong>Columns</strong><span>{profile.columns}</span></div>
            <div><strong>Numeric</strong><span>{profile.numeric_columns?.length || 0}</span></div>
            <div><strong>Categorical</strong><span>{profile.categorical_columns?.length || 0}</span></div>
            <div><strong>Datetime</strong><span>{profile.datetime_columns?.length || 0}</span></div>
          </div>
        ) : (
          <p>Select a dataset to inspect its profile.</p>
        )}
      </section>

      <section className="panel chat-panel">
        <h2>Chat</h2>
        <div className="messages">
          {messages.map((message, index) => (
            <div key={`${message.role}-${index}`} className={`message ${message.role}`}>
              <strong>{message.role === 'user' ? 'You' : 'AI'}</strong>
              <p>{message.content}</p>
            </div>
          ))}
          {loading && <div className="message assistant"><strong>AI</strong><p>Thinking...</p></div>}
        </div>
        <form onSubmit={handleSend} className="chat-form">
          <input value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Ask something about the dataset..." />
          <button type="submit">Send</button>
        </form>
      </section>
    </div>
  )
}

export default App
