package io;

import java.io.FileWriter;
import java.io.IOException;
import java.util.List;

public class CsvWriter {
    public static void writeLabels(String filePath, List<String> labels) throws IOException {
        FileWriter writer = new FileWriter(filePath);
        writer.write("Signal_Label\n");
        for (String label : labels) {
            writer.write(label + "\n");
        }
        writer.close();
    }
}
