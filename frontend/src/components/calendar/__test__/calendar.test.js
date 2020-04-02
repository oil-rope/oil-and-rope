import React from 'react';
import { render, cleanup } from '@testing-library/react';
import Calendar from '../Calendar';
import '@testing-library/jest-dom/extend-expect';

// Cleaning up the rendered DOM
afterEach(cleanup);

it("Renders without problem", () => {
    const { getByTestId } = render(<Calendar />);
    expect(getByTestId('calendar')).not.toBeNull();
});
