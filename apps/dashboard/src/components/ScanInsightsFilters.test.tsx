// @vitest-environment jsdom
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import { describe, expect, it, vi, afterEach } from 'vitest';
import ScanInsightsFilters, {
  scoreBandToRange,
  type ScanInsightsFilterState,
} from './ScanInsightsFilters';

const DEFAULT_FILTERS: ScanInsightsFilterState = {
  scoreBand: 'All',
  sourceFilter: 'All',
  roleFilter: 'All',
  seniorityFilter: 'All',
  missingSkillFilter: 'All',
  belowThresholdOnly: false,
};

describe('ScanInsightsFilters Component & Actions', () => {
  afterEach(cleanup);

  it('renders score band select, source select, role select, missing skill select, and below threshold checkbox', () => {
    render(
      <ScanInsightsFilters
        filters={DEFAULT_FILTERS}
        sources={['RemoteOK', 'Greenhouse']}
        roles={['Backend Engineer', 'Platform Engineer']}
        missingSkills={['Kubernetes', 'Go']}
        onChange={vi.fn()}
      />,
    );

    expect(screen.getByText('All Score Bands')).toBeDefined();
    expect(screen.getByText('All Sources')).toBeDefined();
    expect(screen.getByText('All Roles')).toBeDefined();
    expect(screen.getByText(/Below 75% only/i)).toBeDefined();
  });

  it('triggers onChange when user selects a role filter', () => {
    const handleChange = vi.fn();

    render(
      <ScanInsightsFilters
        filters={DEFAULT_FILTERS}
        sources={['RemoteOK']}
        roles={['Backend Engineer', 'Platform Engineer']}
        missingSkills={[]}
        onChange={handleChange}
      />,
    );

    const selects = screen.getAllByRole('combobox');
    const roleSelect = selects[2]; // Third select is roleFilter
    fireEvent.change(roleSelect, { target: { value: 'Platform Engineer' } });

    expect(handleChange).toHaveBeenCalledWith({ roleFilter: 'Platform Engineer' });
  });

  it('triggers onChange when user toggles below threshold checkbox', () => {
    const handleChange = vi.fn();

    render(
      <ScanInsightsFilters
        filters={DEFAULT_FILTERS}
        sources={[]}
        roles={[]}
        missingSkills={[]}
        onChange={handleChange}
      />,
    );

    const checkbox = screen.getByRole('checkbox');
    fireEvent.click(checkbox);

    expect(handleChange).toHaveBeenCalledWith({ belowThresholdOnly: true });
  });

  it('scoreBandToRange helper maps score bands accurately', () => {
    expect(scoreBandToRange('0-50')).toEqual({ minScore: 0, maxScore: 50 });
    expect(scoreBandToRange('75+')).toEqual({ minScore: 75 });
    expect(scoreBandToRange('All')).toEqual({});
  });
});
