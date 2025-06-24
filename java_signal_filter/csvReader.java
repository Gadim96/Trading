package io;

import model.Signal;
import java.io.*;
import java.util.*;

public class CsvReader {
    public static List<Signal> readSignals(String filePath) throws IOException {
        List<Signal> signals = new ArrayList<>();
        BufferedReader reader = new BufferedReader(new FileReader(filePath));
        reader.readLine(); // skip header

        String line;
        while ((line = reader.readLine()) != null) {
            String[] parts = line.split(",");
            double conf = Double.parseDouble(parts[0]);
            double gap = Double.parseDouble(parts[1]);
            int pred = Integer.parseInt(parts[2]);
            signals.add(new Signal(conf, gap, pred));
        }

        return signals;
    }
}
