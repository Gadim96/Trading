import core.SignalFilter;
import io.CsvReader;
import io.CsvWriter;
import model.Signal;

import java.util.List;

public class Main {
    public static void main(String[] args) {
        String inputFile = "signals.csv";
        String outputFile = "labeled_signals.csv";

        try {
            List<Signal> signals = CsvReader.readSignals(inputFile);

            SignalFilter filter = new SignalFilter(0.7, 0.2);
            List<String> labels = filter.filterSignals(signals);

            CsvWriter.writeLabels(outputFile, labels);
            System.out.println("✅ Labels written to " + outputFile);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
