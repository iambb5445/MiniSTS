import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()
    filename = args.filename
    with open(filename, 'r') as f:
        lines = f.readlines()
    wrong_format_count = 0
    wrong_range_count = 0
    response_times = []
    for line in lines:
        words = line.split()
        if "wrong_format_count" in line:
            wrong_format_count += int(words[-1][:-1])
        elif "wrong_range_count" in line:
            wrong_range_count += int(words[-1])
        elif words[-1][-1] == ',' and words[-1][-2] != ']':
            response_times.append(float(words[-1][:-1]))
    print(wrong_format_count)
    print(wrong_range_count)
    print(len(response_times))
    print(100*(wrong_format_count + wrong_range_count)/len(response_times))
    print(sum(response_times)/len(response_times))

if __name__ == '__main__':
    main()