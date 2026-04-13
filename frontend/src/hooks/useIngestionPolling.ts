import { useCallback, useRef } from 'react';

import { getIngestionJobStatus, type IngestionJobStatusPayload } from '@/services/api';

const sleep = (milliseconds: number) => new Promise((resolve) => {
  setTimeout(resolve, milliseconds);
});

export const useIngestionPolling = () => {
  const stoppedRef = useRef(false);

  const stop = useCallback(() => {
    stoppedRef.current = true;
  }, []);

  const poll = useCallback(async (
    jobId: string,
    maxAttempts = 90,
    onUpdate?: (status: IngestionJobStatusPayload) => void,
  ): Promise<IngestionJobStatusPayload> => {
    stoppedRef.current = false;
    let attempts = 0;
    let status = await getIngestionJobStatus(jobId);
    if (onUpdate) {
      onUpdate(status);
    }

    while (!stoppedRef.current && (status.status === 'queued' || status.status === 'processing') && attempts < maxAttempts) {
      await sleep(1200);
      status = await getIngestionJobStatus(jobId);
      if (onUpdate) {
        onUpdate(status);
      }
      attempts += 1;
    }

    return status;
  }, []);

  return { poll, stop };
};
