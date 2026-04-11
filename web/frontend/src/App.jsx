import { Routes, Route, Navigate } from 'react-router-dom'
import CommandCenter from './layouts/CommandCenter'
import Home from './pages/Home'
import Placeholder from './pages/Placeholder'
import Spending from './pages/finance/Spending'
import Overview from './pages/finance/Overview'
import Forecast from './pages/finance/Forecast'
import Calendar from './pages/finance/Calendar'
import Projection from './pages/finance/Projection'
import Bills from './pages/finance/Bills'
import DashboardV2 from './pages/finance/DashboardV2'
import BillsDetailV2 from './pages/finance/BillsDetailV2'
import BillsTimeline from './pages/finance/BillsTimeline'
import Transactions from './pages/finance/Transactions'
import PatternMatcher from './pages/finance/PatternMatcher'
import PeopleList from './pages/people/PeopleList'
import PersonDetail from './pages/people/PersonDetail'
import RolodexBrowse from './pages/rolodex/RolodexBrowse'
import RolodexDetail from './pages/rolodex/RolodexDetail'
import IrisSystems from './pages/iris/IrisSystems'
import SDIPDashboard from './pages/sdip/SDIPDashboard'
import TransitPressureAdge from './pages/transits/TransitPressureAdge'
import TransitPressureSeraphe from './pages/transits/TransitPressureSeraphe'
export default function App() {
  return (
    <Routes>
      <Route element={<CommandCenter />}>
        {/* Root → Home */}
        <Route path="/" element={<Home />} />
        <Route path="/home" element={<Home />} />
        {/* Finance v2 (new) */}
        <Route path="/finance/dashboard" element={<DashboardV2 />} />
        <Route path="/finance/bills-detail" element={<BillsDetailV2 />} />

        {/* Finance (live) */}
        <Route path="/finance" element={<Navigate to="/finance/dashboard" replace />} />
        <Route path="/finance/overview" element={<Overview />} />
        <Route path="/finance/spending" element={<Spending />} />
        <Route path="/finance/forecast" element={<Forecast />} />
        <Route path="/finance/calendar" element={<Calendar />} />
        <Route path="/finance/projection" element={<Projection />} />
        <Route path="/finance/transactions" element={<Transactions />} />
        <Route path="/finance/bills" element={<Bills />} />
        <Route path="/finance/bills-map" element={<BillsTimeline />} />
        <Route path="/finance/pattern-matcher" element={<PatternMatcher />} />
        <Route path="/finance/categories" element={<Placeholder title="Categories" />} />
        <Route path="/finance/accounts" element={<Placeholder title="Accounts" />} />
        {/* Rolodex (live) */}
        <Route path="/rolodex" element={<Navigate to="/rolodex/browse" replace />} />
        <Route path="/rolodex/browse" element={<RolodexBrowse />} />
        <Route path="/rolodex/node/:cid" element={<RolodexDetail />} />
        {/* People (live) */}
        <Route path="/people" element={<Navigate to="/people/list" replace />} />
        <Route path="/people/list" element={<PeopleList />} />
        <Route path="/people/:eid" element={<PersonDetail />} />
        {/* Iris (live) */}
        <Route path="/iris" element={<IrisSystems />} />
        {/* SDIP */}
        <Route path="/sdip" element={<SDIPDashboard />} />

        {/* Transits (live) */}
        <Route path="/transits" element={<Navigate to="/transits/kataurel" replace />} />
        <Route path="/transits/kataurel" element={<TransitPressureAdge />} />
        <Route path="/transits/seraphe" element={<TransitPressureSeraphe />} />

        {/* Research (stub) */}
        <Route path="/research" element={<Placeholder title="Research" subtitle="Astrology, numerology, soul stratigraphy — migrating" />} />
        {/* Registry (stub) */}
        <Route path="/registry" element={<Placeholder title="Registry" subtitle="The 144 — migrating" />} />
        {/* Sessions (stub) */}
        <Route path="/sessions" element={<Placeholder title="Sessions" subtitle="Transmission logs — migrating" />} />
        {/* Ontology (stub) */}
        <Route path="/ontology" element={<Placeholder title="Ontology" subtitle="Orders, bloodlines, entities — migrating" />} />
        {/* System (stub) */}
        <Route path="/system" element={<Placeholder title="System" subtitle="Arcturus status — migrating" />} />
        {/* Quotes (stub) */}
        <Route path="/quotes" element={<Placeholder title="Quotes" subtitle="Collected transmissions — migrating" />} />
        {/* Catch-all */}
        <Route path="*" element={<Placeholder title="404" subtitle="Not found" />} />
      </Route>
    </Routes>
  )
}
