import { spawn } from 'child_process';

export async function answerQuery(documentText: string, userQuery: string) {
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn('python', ['./backend/local_model.py']);

        let output = '';
        let error = '';

        pythonProcess.stdin.write(JSON.stringify({ documentText, userQuery }));
        pythonProcess.stdin.end();

        pythonProcess.stdout.on('data', (data) => {
            output += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            error += data.toString();
        });

        pythonProcess.on('close', (code) => {
            if (code !== 0) {
                console.error(`Python script exited with code ${code}, error: ${error}`);
                reject(new Error(`Python script failed: ${error}`));
            } else {
                resolve(output.trim());
            }
        });
    });
}