import { T, mono, serif } from '../../styles/theme'
import PageHeader from '../../components/ui/PageHeader'
import EmptyState from '../../components/ui/EmptyState'

/**
 * PatternMatcher — bill-to-transaction matching UI
 * Placeholder for SYS-0039 (foundation). Full build in SYS-0040.
 */
export default function PatternMatcher() {
  return (
    <div>
      <PageHeader
        title="Pattern Matcher"
        subtitle="Match bills to transactions"
        icon="⟁"
        color={T.purple}
      />
      <EmptyState
        icon="⟁"
        title="Coming in SYS-0040"
        message="Split-pane bill matcher with pattern learning. Foundation components deployed."
      />
    </div>
  )
}
