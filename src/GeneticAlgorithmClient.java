import javax.swing.*;
import java.awt.*;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.util.Arrays;

public class GeneticAlgorithmClient extends JFrame {
    private final JTextField usernameField;
    private final JTextField[] choiceFields;
    private final JButton submitButton;
    private final JTextArea resultArea;

    private Socket socket;
    private PrintWriter out;
    private BufferedReader in;

    public GeneticAlgorithmClient() {
        setTitle("Genetic Algorithm Client");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout());
        setPreferredSize(new Dimension(400, 300));

        JPanel inputPanel = new JPanel();
        inputPanel.setLayout(new GridLayout(6, 2));
        inputPanel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        JLabel usernameLabel = new JLabel("Username");
        usernameField = new JTextField();
        inputPanel.add(usernameLabel);
        inputPanel.add(usernameField);

        JLabel[] choiceLabels = new JLabel[4];
        choiceFields = new JTextField[4];
        for (int i = 0; i < 4; i++) {
            choiceLabels[i] = new JLabel("Choice " + (i + 1));
            choiceFields[i] = new JTextField();
            inputPanel.add(choiceLabels[i]);
            inputPanel.add(choiceFields[i]);
        }

        submitButton = new JButton("Submit");
        submitButton.setBackground(new Color(0, 120, 215));
        submitButton.setForeground(Color.WHITE);
        submitButton.addActionListener(e -> submitChoices());

        JPanel buttonPanel = new JPanel();
        buttonPanel.add(submitButton);

        resultArea = new JTextArea();
        resultArea.setEditable(false);
        resultArea.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        JScrollPane scrollPane = new JScrollPane(resultArea);

        add(inputPanel, BorderLayout.NORTH);
        add(buttonPanel, BorderLayout.CENTER);
        add(scrollPane, BorderLayout.SOUTH);

        pack();
        setLocationRelativeTo(null);
    }
    private void submitChoices() {
        try {
            // Connect to the server
            socket = new Socket("localhost", 8080);
            out = new PrintWriter(socket.getOutputStream(), true);
            in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
    
            // Get the username and send it to the server
            String username = usernameField.getText();
            out.println(username);
    
            // Send student choices to the server
            String[] choices = new String[4];
            for (int i = 0; i < 4; i++) {
                String choice = choiceFields[i].getText().trim();
                String value = choice.substring(choice.indexOf(':') + 1).trim();
                choices[i] = value;
            }
            out.println(String.join(",", choices));
    
            // Disable the submit button
            submitButton.setEnabled(false);
    
            // Receive and show the best allocation data
            StringBuilder bestAllocationData = new StringBuilder();
            String line;
            while ((line = in.readLine()) != null) {
                bestAllocationData.append(line).append("\n");
            }
            showBestAllocationTab(bestAllocationData.toString());
    
            // Close the connections
            in.close();
            out.close();
            socket.close();
    
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    } 
    
    private void showBestAllocationTab(String bestAllocationData) {
        JPanel bestAllocationPanel = new JPanel(new BorderLayout());
        JTextArea bestAllocationTextArea = new JTextArea(bestAllocationData);
        bestAllocationTextArea.setEditable(false);
        bestAllocationTextArea.setFont(new Font("Segoe UI", Font.PLAIN, 16));
        bestAllocationTextArea.setBackground(Color.WHITE);
        bestAllocationTextArea.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));
        JScrollPane scrollPane = new JScrollPane(bestAllocationTextArea);
        scrollPane.setHorizontalScrollBarPolicy(ScrollPaneConstants.HORIZONTAL_SCROLLBAR_NEVER);
        scrollPane.setVerticalScrollBarPolicy(ScrollPaneConstants.VERTICAL_SCROLLBAR_NEVER);


        bestAllocationPanel.add(scrollPane, BorderLayout.CENTER);
        bestAllocationTextArea.setLineWrap(false);
        bestAllocationTextArea.setWrapStyleWord(false);
        JLabel titleLabel = new JLabel("Allocation Results");
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 20));
        titleLabel.setForeground(new Color(0, 120, 215));
        titleLabel.setBorder(BorderFactory.createEmptyBorder(20, 20, 10, 20));

        JPanel containerPanel = new JPanel(new BorderLayout());
        containerPanel.setBackground(Color.WHITE);
        containerPanel.add(titleLabel, BorderLayout.NORTH);
        containerPanel.add(bestAllocationPanel, BorderLayout.CENTER);

        getContentPane().removeAll();
        getContentPane().setLayout(new BorderLayout());
        getContentPane().add(containerPanel, BorderLayout.CENTER);
        revalidate();
        repaint();
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            GeneticAlgorithmClient client = new GeneticAlgorithmClient();
            client.setVisible(true);
        });
    }
}
