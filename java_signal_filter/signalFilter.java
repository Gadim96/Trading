package core;

import model.Signal;

import java.util.List;
import java.util.concurrent.*;
import java.util.logging.Logger;
import java.util.stream.Collectors;

public class SignalFilter {
    private static final Logger logger = Logger.getLogger(SignalFilter.class.getName());

    private final double confidenceThreshold;
    private final double gapThreshold;

    public SignalFilter(double confidenceThreshold, double gapThreshold) {
        this.confidenceThreshold = confidenceThreshold;
        this.gapThreshold = gapThreshold;
    }

    public List<String> filterSignals(List<Signal> signals) {
        logger.info("Filtering " + signals.size() + " signals...");

        return signals.parallelStream()
            .map(signal -> signal.getLabel(confidenceThreshold, gapThreshold))
            .collect(Collectors.toList());
    }
}
