import { createBrowserRouter } from 'react-router-dom';
import App from '../App';
import About from '../pages/About';
import HowItWorks from '../pages/HowItWorks';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
  },
  {
    path: '/about',
    element: <About />,
  },
  {
    path: '/how-it-works',
    element: <HowItWorks />,
  },
]);