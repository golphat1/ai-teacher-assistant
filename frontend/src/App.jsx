import { BrowserRouter } from 'react-router-dom';
import Header from './components/layout/Header';
import PageContainer from './components/layout/PageContainer';
import AppRoutes from './routes/AppRoutes';
import DevTokenBanner from './components/layout/DevTokenBanner';

<BrowserRouter>
  <div className="min-h-screen bg-slate-50">
    <DevTokenBanner />
    <Header />
    <PageContainer>
      <AppRoutes />
    </PageContainer>
  </div>
</BrowserRouter>

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50">
        <Header />
        <PageContainer>
          <AppRoutes />
        </PageContainer>
      </div>
    </BrowserRouter>
  );
}