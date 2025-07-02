import { BrowserRouter, Route, Routes } from "react-router-dom"
import Home from "./pages/Home"
import { Userpage } from "./pages/UserPage"

function App() {
  return (
    <BrowserRouter>
    <Routes>
      <Route path='/' element={<Home/>}/>
      <Route path='/user' element={<Userpage/>}/>
    </Routes>
    </BrowserRouter>
  )
}

export default App
