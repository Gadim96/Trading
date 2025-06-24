package model;

public class Signal {
    private final double confidence;
    private final double gap;
    private final int prediction;

    public Signal(double confidence, double gap, int prediction) {
        this.confidence = confidence;
        this.gap = gap;
        this.prediction = prediction;
    }

    public double getConfidence() { return confidence; }
    public double getGap() { return gap; }
    public int getPrediction() { return prediction; }

    public boolean isLong(double threshold, double gapThreshold) {
        return prediction == 2 && confidence > threshold && gap > gapThreshold;
    }

    public boolean isShort(double threshold, double gapThreshold) {
        return prediction == 0 && confidence > threshold && gap > gapThreshold;
    }

    public String getLabel(double confThresh, double gapThresh) {
        if (isLong(confThresh, gapThresh)) return "Long";
        if (isShort(confThresh, gapThresh)) return "Short";
        return "Flat";
    }
}
